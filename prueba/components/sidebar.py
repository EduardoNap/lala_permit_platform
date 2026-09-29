"""Navegación de la barra lateral."""

import reflex as rx

from ..data import NAV_ITEMS
from ..state import State


def sidebar_item(item: dict) -> rx.Component:
    is_active = State.active_page == item["key"]
    content = rx.hstack(
        rx.icon(
            item["icon"],
            size=18,
            color=rx.cond(is_active, "#0f172a", "#64748b"),
        ),
        rx.text(
            item["label"],
            font_size="14px",
            display={"base": "none", "md": "block"},
        ),
        spacing="3",
        align="center",
        width="100%",
        padding="10px 14px",
        border_radius="12px",
        border=rx.cond(is_active, "1px solid rgba(15, 23, 42, 0.08)", "1px solid transparent"),
        background=rx.cond(is_active, "rgba(15, 23, 42, 0.06)", "transparent"),
        color=rx.cond(is_active, "#0f172a", "#475569"),
        box_shadow=rx.cond(
            is_active,
            "0 8px 18px rgba(15, 23, 42, 0.08)",
            "none",
        ),
        _hover={
            "background": "rgba(15, 23, 42, 0.05)",
            "color": "#0f172a",
            "boxShadow": "0 8px 18px rgba(15, 23, 42, 0.08)",
            "transform": "translateY(-1px)",
        },
        transition="all 0.2s ease",
    )
    if item.get("disabled"):
        return rx.box(content, opacity="0.45")
    if item.get("href"):
        on_click = (
            State.start_new_permit
            if item.get("key") == "cargar-permiso"
            else State.set_active_page(item["key"])
        )
        return rx.link(
            content,
            href=item["href"],
            underline="none",
            width="100%",
            on_click=on_click,
        )
    return content


def sidebar() -> rx.Component:
    about_item = next((item for item in NAV_ITEMS if item["key"] == "about"), None)
    main_items = [item for item in NAV_ITEMS if item["key"] != "about"]
    nav_items = [sidebar_item(item) for item in main_items]
    return rx.box(
        rx.flex(
            rx.hstack(
                rx.image(
                    src="/LALA.png",
                    alt="Logo de la empresa",
                    height="82px",
                    width="auto",
                ),
                spacing="3",
                align="center",
                justify="center",
                width="100%",
            ),
            rx.vstack(*nav_items, spacing="2", width="100%"),
            rx.spacer(),
            rx.vstack(
                sidebar_item(about_item),
                width="100%",
            )
            if about_item
            else rx.box(),
            direction="column",
            spacing="6",
            align="start",
            width="100%",
            height="100%",
        ),
        width={"base": "72px", "md": "260px"},
        height="100vh",
        overflow_y="auto",
        overflow_x="hidden",
        background="white",
        padding="24px 18px",
        position="sticky",
        top="0",
        border_right="1px solid rgba(15, 23, 42, 0.08)",
        box_shadow="8px 0 24px rgba(15, 23, 42, 0.04)",
    )
