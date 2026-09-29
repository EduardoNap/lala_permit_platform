"""Extracción de campos desde PDF usando AWS Textract y Amazon Bedrock."""
# Hola

from __future__ import annotations

import json
import os
import re
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

AWS_REGION_DEFAULT = "us-east-2"
# Usa siempre esta región para Textract, ignorando perfiles por defecto.
TEXTRACT_REGION = os.getenv("TEXTRACT_REGION", AWS_REGION_DEFAULT)
from pydantic import BaseModel, ConfigDict, Field

from .storage import build_s3_key, get_s3_config, upload_pdf_bytes


class GovFields(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    nombre: Optional[str] = Field(
        default=None,
        description="Nombre del permiso otorgado por la autoridad gubernamental",
        alias="asunto",
    )
    registro: Optional[str] = Field(
        default=None,
        description="Registro del permiso otorgado por la autoridad gubernamental",
    )
    fecha_emision: Optional[str] = Field(
        default=None,
        description="Fecha de emisión del permiso otorgado por la autoridad gubernamental",
    )
    vigencia: Optional[str] = Field(
        default=None,
        description="Fecha de vigencia del permiso otorgado por la autoridad gubernamental",
    )
    gobierno: Optional[str] = Field(
        default=None,
        description="Nombre del gobierno/estado que emitió el permiso",
    )
    numero: Optional[str] = Field(
        default=None,
        description="Número del permiso otorgado por la autoridad gubernamental",
    )
    nra: Optional[str] = Field(
        default=None,
        description="Número NRA del permiso otorgado por la autoridad gubernamental",
        alias="NRA",
    )
    bitacora: Optional[str] = Field(
        default=None,
        description="Clave o folio de bitácora del permiso",
    )
    condicionantes: list[str] = Field(
        default_factory=list,
        description="Lista de obligaciones o condiciones del permiso",
    )
    evidence: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Evidencia por campo con fragmentos literales del OCR",
    )


def _resolve_region(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return None


@lru_cache
def _get_textract_client(region_name: str | None = None):
    kwargs: dict[str, Any] = {}
    kwargs["region_name"] = region_name or AWS_REGION_DEFAULT
    return boto3.client("textract", **kwargs)


@lru_cache
def _get_bedrock_client(region_name: str | None = None):
    kwargs: dict[str, Any] = {}
    kwargs["region_name"] = region_name or AWS_REGION_DEFAULT
    return boto3.client("bedrock-runtime", **kwargs)


def _textract_blocks_to_lines(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for block in blocks:
        if block.get("BlockType") != "LINE":
            continue
        text = block.get("Text", "").strip()
        if not text:
            continue
        bbox = block.get("Geometry", {}).get("BoundingBox", {})
        lines.append(
            {
                "text": text,
                "page": int(block.get("Page") or 1),
                "bbox": {
                    "left": float(bbox.get("Left", 0.0)),
                    "top": float(bbox.get("Top", 0.0)),
                    "width": float(bbox.get("Width", 0.0)),
                    "height": float(bbox.get("Height", 0.0)),
                },
            }
        )
    return lines


def _textract_lines_to_text(lines: list[dict[str, Any]]) -> str:
    return "\n".join([line["text"] for line in lines if line.get("text")])


def _textract_async_blocks_s3(
    payload: bytes,
    filename: str,
    region_name: str | None,
) -> list[dict[str, Any]]:
    config = get_s3_config()
    if not config:
        raise ValueError("S3 no esta configurado para Textract asincrono.")
    # Fuerza región de Textract a TEXTRACT_REGION
    region = TEXTRACT_REGION
    key = build_s3_key(filename)
    upload_pdf_bytes(payload, key)

    # Debug: confirma bucket/región/key usados por Textract
    print(
        "Textract call -> bucket:",
        config.bucket,
        "key:",
        key,
        "región:",
        region,
    )

    client = _get_textract_client(region)
    def _is_transient_aws_error(exc: Exception) -> bool:
        if isinstance(exc, BotoCoreError):
            return True
        if isinstance(exc, ClientError):
            code = (exc.response.get("Error") or {}).get("Code", "")
            return code in {
                "ThrottlingException",
                "TooManyRequestsException",
                "ProvisionedThroughputExceededException",
                "RequestTimeout",
                "RequestTimeoutException",
                "ServiceUnavailableException",
                "InternalError",
                "InternalServerError",
                "SlowDown",
            }
        return False

    def _call_with_retry(fn, *, max_attempts: int = 3):
        backoff = 1.0
        for attempt in range(1, max_attempts + 1):
            try:
                return fn()
            except Exception as exc:
                if attempt >= max_attempts or not _is_transient_aws_error(exc):
                    raise
                time.sleep(backoff)
                backoff = min(backoff * 2, 8.0)

    response = _call_with_retry(
        lambda: client.start_document_text_detection(
            DocumentLocation={"S3Object": {"Bucket": config.bucket, "Name": key}}
        ),
        max_attempts=3,
    )
    job_id = response["JobId"]

    timeout_seconds = float(os.getenv("TEXTRACT_ASYNC_TIMEOUT", "200"))
    base_poll = float(os.getenv("TEXTRACT_ASYNC_POLL_INTERVAL", "2"))
    poll_interval = max(base_poll, 0.5)
    max_poll = float(os.getenv("TEXTRACT_ASYNC_POLL_MAX", "8"))
    start_time = time.monotonic()
    status = "IN_PROGRESS"
    first_page: dict[str, Any] | None = None

    while status == "IN_PROGRESS":
        try:
            result = client.get_document_text_detection(JobId=job_id)
        except Exception as exc:
            if not _is_transient_aws_error(exc):
                raise
            if time.monotonic() - start_time > timeout_seconds:
                raise TimeoutError("Textract async job timed out.")
            time.sleep(poll_interval)
            poll_interval = min(poll_interval * 1.5, max_poll)
            continue
        status = result.get("JobStatus", "IN_PROGRESS")
        if status in {"SUCCEEDED", "PARTIAL_SUCCESS"}:
            first_page = result
            break
        if status == "FAILED":
            message = result.get("StatusMessage", "Textract job failed.")
            raise RuntimeError(message)
        if time.monotonic() - start_time > timeout_seconds:
            raise TimeoutError("Textract async job timed out.")
        time.sleep(poll_interval)
        poll_interval = min(poll_interval * 1.5, max_poll)

    if first_page is None:
        raise RuntimeError("Textract async job did not return results.")

    blocks = list(first_page.get("Blocks", []))
    next_token = first_page.get("NextToken")
    while next_token:
        page = _call_with_retry(
            lambda: client.get_document_text_detection(
                JobId=job_id, NextToken=next_token
            ),
            max_attempts=3,
        )
        blocks.extend(page.get("Blocks", []))
        next_token = page.get("NextToken")

    return blocks


def pdf_to_lines(pdf_path: Path, region_name: str | None = None) -> list[dict[str, Any]]:
    if region_name is None:
        region_name = _resolve_region("TEXTRACT_REGION", "AWS_REGION", "AWS_DEFAULT_REGION") or AWS_REGION_DEFAULT
    payload = pdf_path.read_bytes()
    if not payload:
        return []
    header_index = payload.find(b"%PDF-")
    if header_index == -1 or header_index > 1024:
        raise ValueError("El archivo no parece ser un PDF valido (cabecera %PDF-).")
    tail = payload[-4096:] if len(payload) > 4096 else payload
    if b"/Encrypt" in tail:
        raise ValueError("El PDF parece estar cifrado/protegido y Textract no lo soporta.")

    if not get_s3_config():
        raise ValueError("S3 no esta configurado para Textract asincrono.")
    blocks = _textract_async_blocks_s3(payload, pdf_path.name, region_name)
    return _textract_blocks_to_lines(blocks)


def pdf_to_text(pdf_path: Path, region_name: str | None = None) -> str:
    return _textract_lines_to_text(pdf_to_lines(pdf_path, region_name=region_name))


def render_pdf_pages(
    pdf_path: Path,
    output_dir: Path,
    prefix: str,
    dpi: int = 150,
) -> list[dict[str, Any]]:
    import fitz

    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    pages: list[dict[str, Any]] = []
    for page_number, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=matrix)
        filename = f"{prefix}_page_{page_number}.png"
        output_path = output_dir / filename
        pix.save(output_path)
        pages.append(
            {
                "page": page_number,
                "file": filename,
                "id": f"upload-page-{page_number}",
            }
        )
    return pages


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    text = text.replace(",", " ").strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        return text
    text = re.sub(r"\s+", " ", text)
    if any(sep in text for sep in ["/", "-", "."]):
        parts = re.split(r"[./-]", text)
        if len(parts) == 3 and all(part.isdigit() for part in parts):
            first, second, third = parts
            if len(first) == 4:
                year, month, day = first, second, third
            elif len(third) == 4:
                day, month, year = first, second, third
            else:
                return None
            if len(day) == 1:
                day = f"0{day}"
            if len(month) == 1:
                month = f"0{month}"
            return f"{year}-{month}-{day}"
    month_map = {
        "ene": "01",
        "enero": "01",
        "jan": "01",
        "january": "01",
        "feb": "02",
        "febrero": "02",
        "february": "02",
        "mar": "03",
        "marzo": "03",
        "march": "03",
        "abr": "04",
        "abril": "04",
        "apr": "04",
        "april": "04",
        "may": "05",
        "mayo": "05",
        "jun": "06",
        "junio": "06",
        "june": "06",
        "jul": "07",
        "julio": "07",
        "july": "07",
        "ago": "08",
        "agosto": "08",
        "aug": "08",
        "august": "08",
        "sep": "09",
        "sept": "09",
        "septiembre": "09",
        "september": "09",
        "oct": "10",
        "octubre": "10",
        "october": "10",
        "nov": "11",
        "noviembre": "11",
        "november": "11",
        "dic": "12",
        "diciembre": "12",
        "dec": "12",
        "december": "12",
    }
    match = re.search(
        r"(\d{1,2})\s+de\s+([A-Za-z.]+)\s+(?:de\s+|del\s+)?(\d{4})",
        text,
    )
    if not match:
        match = re.search(r"(\d{1,2})\s+([A-Za-z.]+)\s+(\d{4})", text)
    if match:
        day, month_text, year = match.groups()
        month_key = month_text.strip(".").lower()
        month = month_map.get(month_key)
        if month:
            if len(day) == 1:
                day = f"0{day}"
            return f"{year}-{month}-{day}"
    return text


def _extract_converse_text(response: dict[str, Any]) -> str:
    output = response.get("output", {})
    message = output.get("message", {})
    content_blocks = message.get("content", [])
    texts: list[str] = []
    for block in content_blocks:
        if not isinstance(block, dict):
            continue
        text = block.get("text")
        if isinstance(text, str) and text.strip():
            texts.append(text.strip())
    return "\n".join(texts).strip()


def _parse_json_payload(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if not raw:
        raise ValueError("Bedrock response was empty.")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(raw[start : end + 1])
        raise


def text_to_json_with_llm(
    text: str,
    model_id: str,
    region_name: str | None = None,
    scope: str | None = None,
) -> GovFields:
    if region_name is None:
        region_name = _resolve_region("BEDROCK_REGION", "AWS_REGION", "AWS_DEFAULT_REGION")
    client = _get_bedrock_client(region_name)

    scope_key = (scope or "Estatal").strip().lower()
    if scope_key in {"municipal", "municipio"}:
        scope_label = "Municipal"
        scope_task = (
            "- Extrae: nombre, registro, fecha_emision, vigencia, condicionantes.\n"
            "- registro puede venir como Folio, Número, Autorización No., Oficio No. o similar.\n"
            "- Si un campo no aplica o no aparece, devuelve \"\" (o [] en condicionantes).\n"
        )
    elif scope_key in {"federal", "federacion"}:
        scope_label = "Federal"
        scope_task = (
            "- Extrae: nombre, nra, fecha_emision, bitacora, gobierno.\n"
            "- nra es un número identificado como NRA.\n"
            "- bitacora es clave/folio de bitácora o identificador similar.\n"
            "- Si un campo no aplica o no aparece, devuelve \"\".\n"
        )
    else:
        scope_label = "Estatal"
        scope_task = (
            "- Extrae: nombre, registro, fecha_emision, vigencia, gobierno, numero, condicionantes.\n"
            "- registro: Registro, Clave de Registro, 0.T. XXXX, etc.\n"
            "- numero: Folio, Oficio No., Número, No., etc.\n"
            "- Si un campo no aplica o no aparece, devuelve \"\" (o [] en condicionantes).\n"
        )

    system = f"""
Eres un extractor de datos. Debes producir ÚNICAMENTE un objeto JSON válido que cumpla el schema.

TIPO DE PERMISO: {scope_label}

TAREA:
{scope_task}

DEFINICIONES:
- nombre: nombre/asunto o resolución del documento.
- condicionantes: resumen breve de las condiciones/solicitudes/compromisos que el permiso ordena.
  - Si no hay numeración, sepáralas por viñetas o saltos de línea.
- gobierno: Estado o municipio de la República Mexicana que emitió el permiso.
- fecha_emision: fecha de emisión del permiso.
- vigencia: fecha de vigencia del permiso.
- registro: registro del permiso.
- numero: número del permiso.
- nra: número NRA del permiso.
- bitacora: clave/folio de bitácora.

REGLAS IMPORTANTES:
1) Usa SOLO información explícita en el texto. NO inventes.
2) Si NO encuentras un campo (excepto condicionantes y evidence), devuelve "".
3) condicionantes: resumen breve de las condicionantes, si NO encuentras nada, devuelve [].
4) REGLAS DE FECHAS (OBLIGATORIO):
   - fecha_emision y vigencia deben ser EXACTAMENTE DD/MM/AAAA.
   - "7 de noviembre de 2025" -> "07/11/2025".
   - Si hay rango "del DD de mes de AAAA al DD de mes de AAAA", usa la fecha final como vigencia.
   - Si vigencia es duración ("un año", "12 meses", "90 días") y existe fecha_emision, suma para obtener vigencia.
     - En evidence incluye la frase literal de duración encontrada.
   - Si NO estás seguro, devuelve "" en ese campo.
5) evidence: objeto con evidencias por campo (listas de fragmentos literales <=200 chars).
   - Usa estas llaves exactas: nombre, registro, fecha_emision, vigencia, gobierno, numero,
     nra, bitacora, condicionantes, general.
   - Incluye evidencia literal para cada campo que llenes.
   - Si hay condicionantes, incluye al menos 1 evidencia por condicionante en la lista de condicionantes.
   - general puede quedar [].
   - Las evidencias deben ser copias literales del OCR, sin etiquetas ni texto extra.

FORMATO DE SALIDA:
- Devuelve SOLO el JSON, sin markdown, sin texto extra.
"""

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "nombre": {"type": "string"},
            "registro": {"type": "string"},
            "fecha_emision": {"type": "string"},
            "vigencia": {"type": "string"},
            "gobierno": {"type": "string"},
            "numero": {"type": "string"},
            "nra": {"type": "string"},
            "bitacora": {"type": "string"},
            "condicionantes": {"type": "array", "items": {"type": "string"}},
            "evidence": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nombre": {"type": "array", "items": {"type": "string"}},
                    "registro": {"type": "array", "items": {"type": "string"}},
                    "fecha_emision": {"type": "array", "items": {"type": "string"}},
                    "vigencia": {"type": "array", "items": {"type": "string"}},
                    "gobierno": {"type": "array", "items": {"type": "string"}},
                    "numero": {"type": "array", "items": {"type": "string"}},
                    "nra": {"type": "array", "items": {"type": "string"}},
                    "bitacora": {"type": "array", "items": {"type": "string"}},
                    "condicionantes": {"type": "array", "items": {"type": "string"}},
                    "general": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "nombre",
                    "registro",
                    "fecha_emision",
                    "vigencia",
                    "gobierno",
                    "numero",
                    "nra",
                    "bitacora",
                    "condicionantes",
                    "general",
                ],
            },
        },
        "required": [
            "nombre",
            "registro",
            "fecha_emision",
            "vigencia",
            "gobierno",
            "numero",
            "nra",
            "bitacora",
            "condicionantes",
            "evidence",
        ],
    }

    schema_json = json.dumps(schema, ensure_ascii=True)
    prompt = f"TEXTO OCR:\n{text}\n\nSCHEMA JSON:\n{schema_json}"
    response = client.converse(
        modelId=model_id,
        system=[{"text": system}],
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"temperature": 0, "maxTokens": 1024},
    )

    model_text = _extract_converse_text(response)
    data_dict = _parse_json_payload(model_text)
    debug_flag = os.getenv("BEDROCK_DEBUG_JSON", "").strip().lower()
    if debug_flag in {"1", "true", "yes"}:
        print("[bedrock] raw_response:", model_text)
        print("[bedrock] parsed_json:", json.dumps(data_dict, ensure_ascii=False))

    if "nombre" not in data_dict and "asunto" in data_dict:
        data_dict["nombre"] = data_dict.get("asunto")

    for key in [
        "nombre",
        "registro",
        "fecha_emision",
        "vigencia",
        "gobierno",
        "numero",
        "nra",
        "bitacora",
    ]:
        if data_dict.get(key, "").strip() == "":
            data_dict[key] = None

    value = data_dict.get("condicionantes")
    if isinstance(value, str):
        value = value.strip()
        data_dict["condicionantes"] = [value] if value else []
    elif value is None:
        data_dict["condicionantes"] = []

    evidence_value = data_dict.get("evidence")
    evidence_map: dict[str, list[str]] = {}
    if isinstance(evidence_value, dict):
        for key, items in evidence_value.items():
            if isinstance(items, list):
                evidence_map[key] = [str(item).strip() for item in items if str(item).strip()]
            elif isinstance(items, str):
                cleaned = items.strip()
                evidence_map[key] = [cleaned] if cleaned else []
            else:
                evidence_map[key] = []
    elif isinstance(evidence_value, list):
        evidence_map["general"] = [
            str(item).strip() for item in evidence_value if str(item).strip()
        ]
    elif isinstance(evidence_value, str):
        cleaned = evidence_value.strip()
        evidence_map["general"] = [cleaned] if cleaned else []
    else:
        evidence_map = {}
    for key in [
        "nombre",
        "registro",
        "fecha_emision",
        "vigencia",
        "gobierno",
        "numero",
        "nra",
        "bitacora",
        "condicionantes",
        "general",
    ]:
        evidence_map.setdefault(key, [])
    if "asunto" in evidence_map and not evidence_map.get("nombre"):
        evidence_map["nombre"] = evidence_map.get("asunto", [])
    data_dict["evidence"] = evidence_map

    if data_dict.get("fecha_emision"):
        data_dict["fecha_emision"] = normalize_date(data_dict["fecha_emision"])
    if data_dict.get("vigencia"):
        data_dict["vigencia"] = normalize_date(data_dict["vigencia"])

    return GovFields.model_validate(data_dict)

def extract_gov_fields(
    pdf_path: Path,
    model_id: str | None = None,
    region_name: str | None = None,
    scope: str | None = None,
) -> tuple[GovFields, list[dict[str, Any]]]:
    if model_id is None:
        model_id = os.getenv("BEDROCK_MODEL_ID", "").strip()
        if not model_id:
            raise ValueError("BEDROCK_MODEL_ID must be set to a Bedrock model ID.")

    textract_start = time.perf_counter()
    lines = pdf_to_lines(pdf_path, region_name=region_name)
    textract_elapsed = time.perf_counter() - textract_start
    print(f"[timing] textract completed in {textract_elapsed:.2f}s")
    text = _textract_lines_to_text(lines)
    if not text.strip():
        return GovFields(
            nombre=None,
            registro=None,
            fecha_emision=None,
            vigencia=None,
            gobierno=None,
            numero=None,
            condicionantes=[],
            evidence={},
        ), []

    llm_start = time.perf_counter()
    fields = text_to_json_with_llm(
        text, model_id=model_id, region_name=region_name, scope=scope
    )
    llm_elapsed = time.perf_counter() - llm_start
    print(f"[timing] llm extraction completed in {llm_elapsed:.2f}s")
    print(
        "[evidence]",
        json.dumps(fields.evidence or {}, ensure_ascii=False, indent=2),
    )
    return fields, lines

