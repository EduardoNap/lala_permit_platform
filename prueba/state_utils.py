"""Utilidades del estado."""

from datetime import date, datetime
from difflib import SequenceMatcher
import re
from typing import Callable


def _parse_date_string(value: str) -> date | None:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except (TypeError, ValueError):
            continue
    return None


def status_from_vigencia(value: str | date | None) -> str:
    if isinstance(value, date):
        vigencia_date = value
    else:
        parsed = _parse_date_string(value or "")
        if not parsed:
            return "Vigente"
        vigencia_date = parsed
    today = datetime.now().date()
    days_remaining = (vigencia_date - today).days
    if days_remaining < 0:
        return "Vencido"
    if days_remaining <= 90:
        return "Por vencer"
    return "Vigente"


def _permit_has_fields_pdf(permit: dict) -> bool:
    pdf_items = permit.get("pdf_items")
    if isinstance(pdf_items, list) and pdf_items:
        return any(item.get("kind") == "fields" for item in pdf_items)
    pdfs = permit.get("pdfs")
    if isinstance(pdfs, list):
        return len(pdfs) >= 3
    return False


def status_from_permit(
    permit: dict,
    parse_date: Callable[[str | date | None], date | None] | None = None,
) -> str:
    if not _permit_has_fields_pdf(permit):
        return "Ingresado"
    if parse_date is not None:
        vigencia = permit.get("vigencia")
        if not parse_date(vigencia):
            return "Sin fecha"
    return status_from_vigencia(permit.get("vigencia", ""))


CONDITION_STATUS_LABELS = {
    "no_iniciado": "No iniciado",
    "en_proceso": "En proceso",
    "completado": "Completado",
}

MONTH_LABELS = [
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
]


def _label_condition_status(value: str | None) -> str:
    if not value:
        return CONDITION_STATUS_LABELS["no_iniciado"]
    if value in CONDITION_STATUS_LABELS:
        return CONDITION_STATUS_LABELS[value]
    normalized = value.strip().lower().replace(" ", "_")
    if normalized in CONDITION_STATUS_LABELS:
        return CONDITION_STATUS_LABELS[normalized]
    cleaned = re.sub(r"^\[[^\]]+\]\s*", "", value.strip())
    normalized_clean = cleaned.lower().replace(" ", "_")
    if normalized_clean in CONDITION_STATUS_LABELS:
        return CONDITION_STATUS_LABELS[normalized_clean]
    for key, label in CONDITION_STATUS_LABELS.items():
        if label.lower() == value.strip().lower():
            return label
        if re.sub(r"^\[[^\]]+\]\s*", "", label.lower()) == cleaned.lower():
            return label
    return CONDITION_STATUS_LABELS["no_iniciado"]


def _normalize_condition_status(value: str | None) -> str:
    if not value:
        return "no_iniciado"
    cleaned = value.strip()
    if cleaned in CONDITION_STATUS_LABELS:
        return cleaned
    normalized = cleaned.lower().replace(" ", "_")
    if normalized in CONDITION_STATUS_LABELS:
        return normalized
    cleaned_no_icon = re.sub(r"^\[[^\]]+\]\s*", "", cleaned)
    normalized_no_icon = cleaned_no_icon.lower().replace(" ", "_")
    if normalized_no_icon in CONDITION_STATUS_LABELS:
        return normalized_no_icon
    for key, label in CONDITION_STATUS_LABELS.items():
        if label.lower() == cleaned.lower():
            return key
        if re.sub(r"^\[[^\]]+\]\s*", "", label.lower()) == cleaned_no_icon.lower():
            return key
    return "no_iniciado"


def _condition_counts(permits: list[dict]) -> tuple[int, int]:
    total = 0
    completed = 0
    for permit in permits:
        items = permit.get("condicionantes", [])
        if isinstance(items, str):
            items = [items] if items.strip() else []
        if not isinstance(items, list):
            continue
        for item in items:
            total += 1
            status = ""
            if isinstance(item, dict):
                status = str(item.get("status") or "")
            elif item is not None:
                status = str(item)
            if _normalize_condition_status(status) == "completado":
                completed += 1
    return completed, total


def _condition_status_counts(permits: list[dict]) -> dict[str, int]:
    counts = {
        CONDITION_STATUS_LABELS["no_iniciado"]: 0,
        CONDITION_STATUS_LABELS["en_proceso"]: 0,
        CONDITION_STATUS_LABELS["completado"]: 0,
    }
    for permit in permits:
        items = permit.get("condicionantes", [])
        if isinstance(items, str):
            items = [items] if items.strip() else []
        if not isinstance(items, list):
            continue
        for item in items:
            status = None
            if isinstance(item, dict):
                status = item.get("status")
            elif item is not None:
                status = str(item)
            label = _label_condition_status(status)
            if label in counts:
                counts[label] += 1
    return counts


def _permit_condition_progress(permit: dict) -> tuple[int, int]:
    items = permit.get("condicionantes", [])
    if isinstance(items, str):
        items = [items] if items.strip() else []
    if not isinstance(items, list):
        return 0, 0
    total = 0
    completed = 0
    for item in items:
        total += 1
        status = ""
        if isinstance(item, dict):
            status = str(item.get("status") or "")
        elif item is not None:
            status = str(item)
        if _normalize_condition_status(status) == "completado":
            completed += 1
    return completed, total


def _permit_status_counts(permits: list[dict]) -> dict[str, int]:
    counts = {"Ingresado": 0, "Vigente": 0, "Por vencer": 0, "Vencido": 0}
    for permit in permits:
        status = status_from_permit(permit)
        if status in counts:
            counts[status] += 1
    return counts


def _permit_status_counts_with_missing(
    permits: list[dict],
    parse_date: Callable[[str | date | None], date | None],
) -> dict[str, int]:
    counts = {
        "Ingresado": 0,
        "Vigente": 0,
        "Por vencer": 0,
        "Vencido": 0,
        "Sin fecha": 0,
    }
    for permit in permits:
        status = status_from_permit(permit, parse_date)
        if status in counts:
            counts[status] += 1
    return counts


def _strip_ingresado(counts: dict[str, int]) -> dict[str, int]:
    return {name: value for name, value in counts.items() if name != "Ingresado"}


def _build_percent_mix(
    counts: dict[str, int],
    palette: dict[str, str],
    order: list[str],
) -> list[dict]:
    total = sum(counts.values())
    if total == 0:
        return [
            {
                "name": "Sin datos",
                "value": 0,
                "color": "#e2e8f0",
                "label": "0%",
                "width": "100%",
            }
        ]
    mix: list[dict] = []
    for name in order:
        count = counts.get(name, 0)
        ratio = count / total
        percent = int(round(ratio * 100))
        mix.append(
            {
                "name": name,
                "value": percent,
                "color": palette.get(name, "#e2e8f0"),
                "label": f"{percent}%",
                "width": f"{ratio * 100:.2f}%",
            }
        )
    return mix


def _normalize_match_text(value: str) -> str:
    cleaned = (value or "").strip().lower()
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _date_variants(value: str) -> list[str]:
    if not value:
        return []
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", value)
    if not match:
        return [value]
    year, month, day = match.groups()
    return [value, f"{day}/{month}/{year}", f"{day}-{month}-{year}"]


def _extract_dates_from_text(text: str) -> list[str]:
    if not text:
        return []
    value = text.lower()
    matches: list[str] = []
    for match in re.finditer(r"(\d{4})[./-](\d{1,2})[./-](\d{1,2})", value):
        year, month, day = match.groups()
        matches.append(f"{year}-{int(month):02d}-{int(day):02d}")
    for match in re.finditer(r"(\d{1,2})[./-](\d{1,2})[./-](\d{4})", value):
        day, month, year = match.groups()
        matches.append(f"{year}-{int(month):02d}-{int(day):02d}")
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
    for match in re.finditer(
        r"(\d{1,2})\s+de\s+([a-z.]+)\s+(?:de\s+|del\s+)?(\d{4})",
        value,
    ):
        day, month_text, year = match.groups()
        month = month_map.get(month_text.strip("."))
        if month:
            matches.append(f"{year}-{month}-{int(day):02d}")
    for match in re.finditer(r"(\d{1,2})\s+([a-z.]+)\s+(\d{4})", value):
        day, month_text, year = match.groups()
        month = month_map.get(month_text.strip("."))
        if month:
            matches.append(f"{year}-{month}-{int(day):02d}")
    deduped: list[str] = []
    seen = set()
    for item in matches:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def _match_date_line_indices(target_date: str, lines: list[dict]) -> list[int]:
    if not target_date or not lines:
        return []
    indices: list[int] = []
    for idx, line in enumerate(lines):
        parsed_dates = _extract_dates_from_text(line.get("text", ""))
        if target_date in parsed_dates:
            indices.append(idx)
    return indices


def _evidence_for_targets(targets: list[str], evidence: list[str]) -> list[str]:
    matches: list[str] = []
    if not targets or not evidence:
        return matches
    for snippet in evidence:
        norm_snippet = _normalize_match_text(snippet)
        if not norm_snippet:
            continue
        for target in targets:
            norm_target = _normalize_match_text(target)
            if not norm_target:
                continue
            if norm_target in norm_snippet or norm_snippet in norm_target:
                matches.append(snippet)
                break
            if SequenceMatcher(None, norm_target, norm_snippet).ratio() >= 0.6:
                matches.append(snippet)
                break
    return matches


def _match_line_indices(targets: list[str], lines: list[dict]) -> list[int]:
    if not targets or not lines:
        return []
    norm_lines = [_normalize_match_text(line.get("text", "")) for line in lines]
    indices: set[int] = set()
    for target in targets:
        norm_target = _normalize_match_text(target)
        if not norm_target:
            continue
        best_index: int | None = None
        best_score = 0.0
        direct_hits: list[int] = []
        for idx, norm_line in enumerate(norm_lines):
            if not norm_line:
                continue
            if norm_target in norm_line:
                direct_hits.append(idx)
                if len(direct_hits) >= 3:
                    break
                continue
            score = SequenceMatcher(None, norm_target, norm_line).ratio()
            if score > best_score:
                best_score = score
                best_index = idx
        if direct_hits:
            indices.update(direct_hits)
        elif best_index is not None and best_score >= 0.6:
            indices.add(best_index)
    return sorted(indices)


def _lines_to_boxes(lines: list[dict], indices: list[int]) -> list[dict]:
    boxes: list[dict] = []
    for idx in indices:
        if idx < 0 or idx >= len(lines):
            continue
        line = lines[idx]
        bbox = line.get("bbox", {})
        boxes.append(
            {
                "page": int(line.get("page", 1)),
                "left": f"{float(bbox.get('left', 0.0)) * 100:.2f}%",
                "top": f"{float(bbox.get('top', 0.0)) * 100:.2f}%",
                "width": f"{float(bbox.get('width', 0.0)) * 100:.2f}%",
                "height": f"{float(bbox.get('height', 0.0)) * 100:.2f}%",
                "text": line.get("text", ""),
            }
        )
    return boxes


def _build_upload_field_boxes(
    fields, lines: list[dict], scope: str | None = None
) -> dict[str, list[dict]]:
    evidence_map = fields.evidence or {}
    if "asunto" in evidence_map and not evidence_map.get("nombre"):
        evidence_map["nombre"] = evidence_map.get("asunto", [])
    general_evidence = list(evidence_map.get("general", []))
    field_targets: dict[str, list[str]] = {}
    scope_key = (scope or "Estatal").strip().lower()
    if scope_key in {"municipal", "municipio"}:
        allowed_fields = {
            "nombre",
            "registro",
            "fecha_emision",
            "vigencia",
            "condicionantes",
        }
    elif scope_key in {"federal", "federacion"}:
        allowed_fields = {
            "nombre",
            "nra",
            "bitacora",
            "gobierno",
            "fecha_emision",
        }
    else:
        allowed_fields = {
            "nombre",
            "registro",
            "fecha_emision",
            "vigencia",
            "gobierno",
            "numero",
            "condicionantes",
        }
    if "nombre" in allowed_fields and fields.nombre:
        field_targets["nombre"] = [fields.nombre]
    if "registro" in allowed_fields and fields.registro:
        field_targets["registro"] = [fields.registro]
    if "gobierno" in allowed_fields and fields.gobierno:
        field_targets["gobierno"] = [fields.gobierno]
    if "numero" in allowed_fields and fields.numero:
        field_targets["numero"] = [fields.numero]
    if "nra" in allowed_fields and getattr(fields, "nra", None):
        field_targets["nra"] = [fields.nra]
    if "bitacora" in allowed_fields and getattr(fields, "bitacora", None):
        field_targets["bitacora"] = [fields.bitacora]
    boxes_by_field: dict[str, list[dict]] = {}
    date_fields: dict[str, str] = {}
    if "fecha_emision" in allowed_fields and fields.fecha_emision:
        date_fields["fecha_emision"] = fields.fecha_emision
    if "vigencia" in allowed_fields and fields.vigencia:
        date_fields["vigencia"] = fields.vigencia
    if "condicionantes" in allowed_fields and fields.condicionantes:
        field_targets["condicionantes"] = list(fields.condicionantes)

    for field, date_value in date_fields.items():
        date_indices = _match_date_line_indices(date_value, lines)
        if date_indices:
            boxes_by_field[field] = _lines_to_boxes(lines, date_indices)
        else:
            field_targets[field] = _date_variants(date_value)

    for field, targets in field_targets.items():
        if field in boxes_by_field:
            continue
        field_evidence = list(evidence_map.get(field, []))
        if not field_evidence and general_evidence:
            field_evidence = _evidence_for_targets(targets, general_evidence)
        all_targets = [*targets, *field_evidence]
        indices = _match_line_indices(all_targets, lines)
        if indices:
            boxes_by_field[field] = _lines_to_boxes(lines, indices)
    return boxes_by_field
