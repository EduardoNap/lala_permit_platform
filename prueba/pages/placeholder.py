"""Páginas de marcador para rutas secundarias."""

import reflex as rx

from ..components.layout import page_shell


def placeholder_page(title: str) -> rx.Component:
    return page_shell(
        rx.box(
            rx.card(
                rx.vstack(
                    rx.text(title, font_size="26px", font_weight="600"),
                    rx.text(
                        "Esta página es un marcador. Reemplázala con contenido real.",
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
            ),
            padding="0px 28px 32px 28px",
            width="100%",
        )
    )
