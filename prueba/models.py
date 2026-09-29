"""Modelos tipados para permisos y secciones CEDIS."""

from dataclasses import dataclass, field


@dataclass
class Permit:
    id: int
    nombre: str
    gobierno: str
    fecha_emision: str
    vigencia: str
    numero: str
    cedis: str
    status: str
    responsable: str = ""
    numero_display: str = ""
    permit_scope: str = ""
    nra: str = ""
    bitacora: str = ""
    zona: str = ""
    progress_value: int = 0
    progress_label: str = ""
    progress_color: str = "blue"
    asunto: str = ""
    registro: str = ""
    pdfs: list[str] = field(default_factory=list)
    pdfs_label: str = ""
    pdf_items: list[dict] = field(default_factory=list)


@dataclass
class PermitSection:
    cedis: str
    permits: list[Permit]
    count_label: str
