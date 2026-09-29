"""Listado de tareas por CEDIS."""

import reflex as rx

from ..components.cedis_dashboard import status_badge
from ..components.layout import page_shell
from ..state import State


def _task_detail(label: str, value: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.text(label, font_size="11px", color="#94a3b8"),
        rx.text(value, font_size="12px", color="#475569"),
        spacing="1",
        align="center",
    )


def _task_details_for_scope(row: rx.Var) -> rx.Component:
    return rx.cond(
        row.permit_scope == "Federal",
        rx.flex(
            _task_detail("Nombre:", row.nombre),
            _task_detail("NRA:", row.nra),
            _task_detail("Bitácora:", row.bitacora),
            _task_detail("Gobierno:", row.gobierno),
            _task_detail("Fecha:", row.fecha_emision),
            gap="12px",
            wrap="wrap",
            width="100%",
        ),
        rx.cond(
            row.permit_scope == "Municipal",
            rx.flex(
                _task_detail("Nombre:", row.nombre),
                _task_detail("Registro:", row.registro),
                _task_detail("Fecha:", row.fecha_emision),
                _task_detail("Vigencia:", row.vigencia),
                gap="12px",
                wrap="wrap",
                width="100%",
            ),
            rx.flex(
                _task_detail("Nombre:", row.nombre),
                _task_detail("Registro:", row.registro),
                _task_detail("Gobierno:", row.gobierno),
                rx.cond(
                    row.numero_display != "",
                    _task_detail("Número:", row.numero_display),
                    rx.box(),
                ),
                _task_detail("Fecha:", row.fecha_emision),
                _task_detail("Vigencia:", row.vigencia),
                gap="12px",
                wrap="wrap",
                width="100%",
            ),
        ),
    )


def task_row(row: rx.Var) -> rx.Component:
    card_content = rx.box(
        rx.vstack(
            rx.link(
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.box(
                                rx.icon(
                                    "clipboard-list", size=16, color="#1f3a5f"
                                ),
                                width="30px",
                                height="30px",
                                border_radius="9px",
                                background="rgba(59, 130, 246, 0.12)",
                                display="flex",
                                align_items="center",
                                justify_content="center",
                                flex_shrink="0",
                            ),
                            rx.text(row.nombre, font_size="14px", font_weight="600"),
                            spacing="2",
                            align="center",
                        ),
                        status_badge(row.status),
                        justify="between",
                        align="center",
                        width="100%",
                    ),
                    _task_details_for_scope(row),
                    rx.vstack(
                        rx.hstack(
                            rx.text(
                                "Condicionantes",
                                font_size="11px",
                                color="#64748b",
                            ),
                            rx.text(
                                f"{row.progress_value}%",
                                font_size="11px",
                                color="#64748b",
                            ),
                            justify="between",
                            width="100%",
                        ),
                        rx.progress(
                            value=row.progress_value,
                            max=100,
                            height="7px",
                            border_radius="999px",
                            color_scheme=row.progress_color,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                href="/cedis",
                underline="none",
                width="100%",
                style={"display": "block"},
                on_click=State.select_global_permit(row.cedis, row.id),
            ),
            rx.cond(
                row.progress_value >= 100,
                rx.hstack(
                    rx.button(
                        "Marcar como completado",
                        size="2",
                        variant="soft",
                        color_scheme="green",
                        on_click=State.complete_permit(row.id),
                    ),
                    justify="end",
                    width="100%",
                ),
                rx.box(),
            ),
            spacing="2",
            width="100%",
        ),
        padding="14px 46px 14px 14px",
        width="100%",
    )
    return rx.box(
        card_content,
        border_radius="12px",
        border="1px solid #e2e8f0",
        background="rgba(248, 250, 252, 0.9)",
        _hover={"background": "rgba(241, 245, 249, 0.95)"},
        width="100%",
        position="relative",
    )


def cedis_section(section: rx.Var) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(section.cedis, font_size="16px", font_weight="600"),
                rx.text(section.count_label, font_size="12px", color="#94a3b8"),
                justify="between",
                width="100%",
            ),
            rx.vstack(
                rx.foreach(section.permits, task_row),
                spacing="3",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding="16px",
        border_radius="12px",
        border="1px solid #e5e7eb",
        box_shadow="0 10px 24px rgba(15, 23, 42, 0.06)",
        background="white",
    )


def permits_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("Tareas", font_size="26px", font_weight="600"),
            rx.vstack(
                rx.foreach(State.permits_by_cedis_list, cedis_section),
                spacing="4",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        padding="0px 28px 32px 28px",
        width="100%",
    )


def permits_page() -> rx.Component:
    return page_shell(permits_content())
