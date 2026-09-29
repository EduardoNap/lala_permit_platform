"""Página acerca de la app."""

import reflex as rx

from ..components.cedis_dashboard import status_badge
from ..components.layout import page_shell


def _bullet_item(text: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="6px",
            height="6px",
            border_radius="999px",
            background="#1f3a5f",
        ),
        rx.text(text, font_size="13px", color="#475569"),
        spacing="2",
        align="center",
    )


def _neutral_badge(label: str) -> rx.Component:
    return rx.badge(
        label,
        color="#64748b",
        background="rgba(148, 163, 184, 0.16)",
        font_size="11px",
        border_radius="999px",
        padding="4px 10px",
    )


def _step_item(step: str, title: str, description: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.text(step, font_size="12px", font_weight="600", color="#1f3a5f"),
            width="28px",
            height="28px",
            border_radius="999px",
            border="1px solid rgba(31, 58, 95, 0.25)",
            background="rgba(31, 58, 95, 0.08)",
            display="flex",
            align_items="center",
            justify_content="center",
            flex_shrink="0",
        ),
        rx.vstack(
            rx.text(title, font_size="13px", font_weight="600"),
            rx.text(description, font_size="12px", color="#64748b"),
            spacing="1",
            align="start",
        ),
        spacing="3",
        align="start",
        width="100%",
    )


def _section_tile(
    icon: str,
    title: str,
    description: str,
    detail: str | None = None,
) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=18, color="#1f3a5f"),
                width="32px",
                height="32px",
                border_radius="10px",
                background="rgba(59, 130, 246, 0.12)",
                display="flex",
                align_items="center",
                justify_content="center",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.text(title, font_size="13px", font_weight="600"),
                rx.text(description, font_size="12px", color="#64748b"),
                rx.text(detail, font_size="11px", color="#94a3b8")
                if detail
                else rx.box(),
                spacing="1",
                align="start",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        padding="14px",
        border_radius="12px",
        border="1px solid #e2e8f0",
        background="rgba(248, 250, 252, 0.9)",
        width="100%",
    )


def about_page() -> rx.Component:
    return page_shell(
        rx.box(
            rx.vstack(
                rx.card(
                    rx.vstack(
                        rx.text("Acerca", font_size="26px", font_weight="600"),
                        rx.text(
                            "Guía para monitorear permisos, CEDIS y "
                            "cumplimiento operativo.",
                            font_size="14px",
                            color="#64748b",
                        ),
                        spacing="3",
                        align="start",
                    ),
                    padding="24px",
                    border_radius="12px",
                    border="1px solid #e5e7eb",
                    background="white",
                    box_shadow="0 10px 24px rgba(15, 23, 42, 0.08)",
                    width="100%",
                ),
                rx.grid(
                    rx.card(
                        rx.vstack(
                            rx.text("Qué puedes hacer", font_size="18px", font_weight="600"),
                            rx.vstack(
                                _bullet_item(
                                    "Monitorear el estado de permisos por región y CEDIS."
                                ),
                                _bullet_item(
                                    "Detectar riesgos con KPIs y tendencias de vencimiento."
                                ),
                                _bullet_item(
                                    "Gestionar condicionantes por permiso."
                                ),
                                _bullet_item(
                                    "Cargar permisos y archivos relacionados con extracción automática."
                                ),
                                _bullet_item(
                                    "Consultar historial con filtros por responsable y zona."
                                ),
                                spacing="2",
                                align="start",
                            ),
                            spacing="3",
                            align="start",
                        ),
                        padding="20px",
                        border_radius="12px",
                        border="1px solid #e5e7eb",
                        background="white",
                        box_shadow="0 10px 24px rgba(15, 23, 42, 0.06)",
                        width="100%",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("Flujo recomendado", font_size="18px", font_weight="600"),
                            rx.vstack(
                                _step_item(
                                    "1",
                                    "Revisa el tablero",
                                    "Prioriza permisos por vencer y CEDIS en riesgo.",
                                ),
                                _step_item(
                                    "2",
                                    "Selecciona región y CEDIS",
                                    "Enfoca el tablero y el detalle operativo.",
                                ),
                                _step_item(
                                    "3",
                                    "Gestiona tareas",
                                    "Actualiza condicionantes y avances.",
                                ),
                                _step_item(
                                    "4",
                                    "Carga permisos",
                                    "Sube PDFs y completa campos con o sin extracción.",
                                ),
                                spacing="3",
                                align="start",
                            ),
                            spacing="3",
                            align="start",
                        ),
                        padding="20px",
                        border_radius="12px",
                        border="1px solid #e5e7eb",
                        background="white",
                        box_shadow="0 10px 24px rgba(15, 23, 42, 0.06)",
                        width="100%",
                    ),
                    columns={"base": "1fr", "lg": "1fr 1fr"},
                    gap="16px",
                    width="100%",
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Secciones principales", font_size="18px", font_weight="600"),
                        rx.grid(
                            _section_tile(
                                "layout-dashboard",
                                "Tablero",
                                "KPIs, tendencias de vencimiento y riesgos.",
                                "Visión general del cumplimiento.",
                            ),
                            _section_tile(
                                "building-2",
                                "Regiones / CEDIS",
                                "Selecciona zona y revisa el detalle del CEDIS.",
                                "Incluye edición de información.",
                            ),
                            _section_tile(
                                "file-text",
                                "Tareas",
                                "Listado de permisos y condicionantes por CEDIS.",
                                "Marca completados y avances.",
                            ),
                            _section_tile(
                                "upload",
                                "Cargar permiso",
                                "Flujo guiado para subir PDFs y registrar datos.",
                                "Acuse, pago, permiso y extra.",
                            ),
                            _section_tile(
                                "history",
                                "Historial",
                                "Versiones anteriores y PDFs asociados.",
                                "Filtros por responsable y zona.",
                            ),
                            columns="repeat(auto-fit, minmax(220px, 1fr))",
                            gap="12px",
                            width="100%",
                        ),
                        spacing="3",
                        align="start",
                        width="100%",
                    ),
                    padding="24px",
                    border_radius="12px",
                    border="1px solid #e5e7eb",
                    background="white",
                    box_shadow="0 10px 24px rgba(15, 23, 42, 0.08)",
                    width="100%",
                ),
                rx.grid(
                    rx.card(
                        rx.vstack(
                            rx.text("Estados de permisos", font_size="18px", font_weight="600"),
                            rx.flex(
                                status_badge("Ingresado"),
                                status_badge("Vigente"),
                                status_badge("Por vencer"),
                                status_badge("Vencido"),
                                _neutral_badge("Sin fecha"),
                                wrap="wrap",
                                gap="6px",
                                width="100%",
                            ),
                            rx.vstack(
                                _bullet_item("Ingresado: permiso sin PDF principal."),
                                _bullet_item(
                                    "Vigente: vigencia con más de 90 días restantes."
                                ),
                                _bullet_item(
                                    "Por vencer: vigencia dentro de los próximos 90 días."
                                ),
                                _bullet_item("Vencido: vigencia ya terminó."),
                                _bullet_item("Sin fecha: vigencia no capturada."),
                                spacing="2",
                                align="start",
                            ),
                            spacing="3",
                            align="start",
                        ),
                        padding="20px",
                        border_radius="12px",
                        border="1px solid #e5e7eb",
                        background="white",
                        box_shadow="0 10px 24px rgba(15, 23, 42, 0.06)",
                        width="100%",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("PDFs y datos", font_size="18px", font_weight="600"),
                            rx.vstack(
                                _bullet_item(
                                    "Adjunta acuse, pago, permiso y archivos extras."
                                ),
                                _bullet_item(
                                    "Vista previa y comentarios por cada documento."
                                ),
                                _bullet_item(
                                    "Extracción automática de campos cuando está habilitada."
                                ),
                                _bullet_item(
                                    "El historial conserva versiones anteriores del permiso."
                                ),
                                spacing="2",
                                align="start",
                            ),
                            spacing="3",
                            align="start",
                        ),
                        padding="20px",
                        border_radius="12px",
                        border="1px solid #e5e7eb",
                        background="white",
                        box_shadow="0 10px 24px rgba(15, 23, 42, 0.06)",
                        width="100%",
                    ),
                    columns={"base": "1fr", "lg": "1fr 1fr"},
                    gap="16px",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            padding="0px 28px 32px 28px",
            width="100%",
        ),
        header_overlap=False,
    )
