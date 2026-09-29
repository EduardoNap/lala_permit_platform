"""Historial de permisos actualizados."""

import reflex as rx

from ..components.layout import page_shell
from ..state import State


def history_pdf_icon(item: rx.Var) -> rx.Component:
    file_url = rx.cond(
        State.use_s3,
        item["url"],
        rx.get_upload_url(item["file"]),
    )
    kind = item["kind"]
    background = rx.cond(
        kind == "primary",
        "rgba(59, 130, 246, 0.14)",
        rx.cond(
            kind == "secondary",
            "rgba(245, 158, 11, 0.16)",
            rx.cond(
                kind == "fields",
                "rgba(34, 197, 94, 0.16)",
                "rgba(148, 163, 184, 0.18)",
            ),
        ),
    )
    color = rx.cond(
        kind == "primary",
        "#1d4ed8",
        rx.cond(
            kind == "secondary",
            "#b45309",
            rx.cond(kind == "fields", "#15803d", "#64748b"),
        ),
    )
    return rx.link(
        rx.icon("file-text", size=16, color=color),
        href=file_url,
        is_external=True,
        underline="none",
        title=item["label"],
        _hover={"background": background, "borderRadius": "6px"},
        padding="4px",
    )


def _header_label(text: str) -> rx.Component:
    return rx.hstack(
        rx.text(text, font_size="11px", color="#64748b"),
        rx.icon("chevron-down", size=12, color="#94a3b8"),
        spacing="1",
        align="center",
    )


def _header_cell(content: rx.Component, has_border: bool = True) -> rx.Component:
    return rx.box(
        content,
        border_right="1px solid #e5e7eb" if has_border else "none",
        padding_right="8px",
        width="100%",
    )


def history_header() -> rx.Component:
    input_style = {
        "background": "rgba(255, 255, 255, 0.9)",
        "border": "1px solid #e2e8f0",
        "borderRadius": "6px",
        "fontSize": "11px",
        "height": "24px",
        "padding": "0 6px",
        "color": "#64748b",
        "outline": "none",
    }
    return rx.grid(
        _header_cell(
            rx.vstack(
                _header_label("Nombre"),
                rx.input(
                    placeholder="Buscar",
                    value=State.history_query,
                    on_change=State.set_history_query,
                    style=input_style,
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
        ),
        _header_cell(
            rx.vstack(
                _header_label("Responsable"),
                rx.select(
                    State.history_responsable_options,
                    value=State.history_filter_responsable,
                    on_change=State.set_history_filter_responsable,
                    style=input_style,
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
        ),
        _header_cell(
            rx.vstack(
                _header_label("Región"),
                rx.select(
                    State.history_zona_options,
                    value=State.history_filter_zona,
                    on_change=State.set_history_filter_zona,
                    style=input_style,
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
        ),
        _header_cell(
            rx.vstack(
                _header_label("CEDIS"),
                rx.select(
                    State.history_cedis_options,
                    value=State.history_filter_cedis,
                    on_change=State.set_history_filter_cedis,
                    style=input_style,
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
        ),
        _header_cell(
            rx.vstack(
                _header_label("Vigencia"),
                rx.box(height="24px"),
                spacing="1",
                align="center",
                width="100%",
            ),
        ),
        _header_cell(
            rx.vstack(
                rx.text("PDFs", font_size="11px", color="#64748b"),
                rx.box(height="24px"),
                spacing="1",
                align="center",
                width="100%",
            ),
            has_border=False,
        ),
        columns="1.6fr 1.2fr 1fr 1fr 1.2fr 1.2fr",
        spacing="3",
        align="start",
        padding="12px 12px",
        border_bottom="1px solid #e5e7eb",
        background="rgba(241, 245, 249, 0.95)",
        width="100%",
    )


def history_row(row: rx.Var) -> rx.Component:
    return rx.grid(
        rx.text(
            row.nombre,
            font_size="13px",
            font_weight="600",
            min_width="0",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        rx.text(
            rx.cond(row.responsable == "", "Sin responsable", row.responsable),
            font_size="12px",
            color="#64748b",
            min_width="0",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        rx.text(
            row.zona,
            font_size="12px",
            color="#64748b",
            min_width="0",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        rx.text(
            row.cedis,
            font_size="12px",
            color="#64748b",
            min_width="0",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        rx.text(
            rx.cond(
                (row.fecha_emision == "") & (row.vigencia == ""),
                "Sin fechas",
                rx.cond(
                    row.vigencia == "",
                    row.fecha_emision,
                    rx.cond(
                        row.fecha_emision == "",
                        row.vigencia,
                        f"{row.fecha_emision} - {row.vigencia}",
                    ),
                ),
            ),
            font_size="12px",
            color="#64748b",
            min_width="0",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        rx.cond(
            row.pdfs_label == "",
            rx.flex(
                rx.foreach(row.pdf_items, history_pdf_icon),
                wrap="wrap",
                row_gap="6px",
                column_gap="6px",
                width="100%",
                min_width="0",
            ),
            rx.text(row.pdfs_label, font_size="11px", color="#94a3b8"),
        ),
        columns="1.6fr 1.2fr 1fr 1fr 1.2fr 1.2fr",
        spacing="3",
        align="center",
        padding="10px 12px",
        border_bottom="1px solid #e5e7eb",
        background="white",
        _hover={"background": "rgba(248, 250, 252, 0.95)"},
        width="100%",
    )


def historial_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("Historial", font_size="26px", font_weight="600"),
            rx.text(
                "Permisos anteriores.",
                font_size="12px",
                color="#64748b",
            ),
            rx.box(
                rx.vstack(
                    history_header(),
                    rx.cond(
                        State.has_filtered_permit_history,
                        rx.vstack(
                            rx.foreach(State.filtered_permit_history_items, history_row),
                            spacing="0",
                            width="100%",
                        ),
                        rx.box(
                            rx.text(
                                "Sin permisos en historial",
                                font_size="12px",
                                color="#94a3b8",
                            ),
                            padding="16px",
                            background="white",
                            width="100%",
                        ),
                    ),
                    spacing="0",
                    width="100%",
                ),
                border="1px solid #e5e7eb",
                border_radius="12px",
                overflow="hidden",
                background="white",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        padding="0px 28px 32px 28px",
        width="100%",
    )


def historial_page() -> rx.Component:
    return page_shell(historial_content())
