"""Página de detalle para CEDIS."""

import reflex as rx

from ..components.cedis_dashboard import cedis_overview_card
from ..components.layout import page_shell
from ..state import State


def cedis_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.flex(
                rx.box(
                    rx.vstack(
                        rx.text(
                            "Región",
                            font_size="24px",
                            font_weight="700",
                        ),
                        rx.text(
                            rx.cond(
                                State.selected_zona == "VDM",
                                "Valle de México",
                                State.selected_zona,
                            ),
                            font_size="18px",
                            font_weight="600",
                            color="#1f3a5f",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    width="100%",
                ),
                direction="column",
                gap="8px",
                align="start",
                width="100%",
            ),
            rx.box(cedis_overview_card(), width="100%"),
            spacing="4",
            width="100%",
        ),
        padding="0px 28px 32px 28px",
        width="100%",
        on_mount=State.reset_cedis_view,
    )


def cedis_page() -> rx.Component:
    return page_shell(cedis_content())
