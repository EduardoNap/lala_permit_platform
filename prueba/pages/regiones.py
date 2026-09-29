"""Página de regiones y CEDIS."""

import reflex as rx

from ..components.layout import page_shell
from ..state import State


def region_card(name: rx.Var) -> rx.Component:
    selected = State.region_choice_made & (State.selected_zona == name)
    display_name = rx.cond(name == "VDM", "Valle de México", name)
    image_src = rx.cond(
        name == "Centro",
        "/Centro.png",
        rx.cond(
            name == "Occidente",
            "/occidente.PNG",
            rx.cond(name == "VDM", "/VDM.jpg", "/LALA.png"),
        ),
    )
    return rx.card(
        rx.vstack(
            rx.image(
                src=image_src,
                width="100%",
                height="160px",
                object_fit="cover",
                border_radius="10px",
            ),
            rx.text(display_name, font_size="14px", font_weight="600"),
            rx.link(
                rx.button(
                    "Seleccionar región",
                    size="2",
                    width="100%",
                    background=rx.cond(
                        selected,
                        "#1f3a5f",
                        "rgba(31, 58, 95, 0.12)",
                    ),
                    color=rx.cond(selected, "white", "#1f3a5f"),
                    _hover={
                        "background": "#1f3a5f",
                        "color": "white",
                    },
                ),
                href="/cedis",
                underline="none",
                width="100%",
                on_click=State.select_zona(name),
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
        padding="12px",
        border_radius="12px",
        border=rx.cond(selected, "1px solid #1f3a5f", "1px solid #e5e7eb"),
        box_shadow="0 10px 24px rgba(15, 23, 42, 0.06)",
        background="white",
    )


def regiones_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("Regiones", font_size="26px", font_weight="600"),
            rx.text(
                "Para comenzar, selecciona una región para administrar:",
                font_size="12px",
                color="#64748b",
            ),
            rx.grid(
                rx.foreach(State.zona_locations, region_card),
                columns="repeat(auto-fit, minmax(220px, 1fr))",
                gap="12px",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        padding="0px 28px 32px 28px",
        width="100%",
    )


def regiones_page() -> rx.Component:
    return page_shell(regiones_content())
