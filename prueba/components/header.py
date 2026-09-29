"""Barra superior."""

import reflex as rx

from ..state import State


def notification_item(item: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="8px",
            height="8px",
            border_radius="999px",
            background=rx.cond(item["read"], "#cbd5e1", "#22c55e"),
            flex_shrink="0",
            margin_top="4px",
        ),
        rx.vstack(
            rx.text(item["message"], font_size="12px", font_weight="500"),
            rx.text(item["timestamp"], font_size="10px", color="#94a3b8"),
            spacing="1",
            align="start",
        ),
        spacing="2",
        align="start",
        padding="6px 8px",
        border_radius="8px",
        _hover={"background": "rgba(148, 163, 184, 0.12)"},
        width="100%",
    )


def notifications_panel() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text("Notificaciones", font_size="12px", font_weight="600"),
            rx.spacer(),
            rx.button(
                rx.icon("x", size=12),
                variant="ghost",
                size="1",
                on_click=State.close_notifications,
            ),
            width="100%",
            align="center",
        ),
        rx.box(height="1px", background="#e2e8f0", width="100%"),
        rx.cond(
            State.has_notifications,
            rx.vstack(
                rx.foreach(State.notifications, notification_item),
                spacing="1",
                width="100%",
                max_height="320px",
                overflow="auto",
            ),
            rx.text(
                "Sin notificaciones",
                font_size="11px",
                color="#94a3b8",
                padding="10px 4px",
            ),
        ),
        position="absolute",
        top="calc(100% + 8px)",
        right="0",
        padding="10px",
        border_radius="12px",
        border="1px solid #e5e7eb",
        background="white",
        box_shadow="0 12px 24px rgba(15, 23, 42, 0.12)",
        min_width="320px",
        z_index="30",
    )


def notification_bell() -> rx.Component:
    return rx.box(
        rx.cond(
            State.notifications_open,
            rx.box(
                position="fixed",
                top="0",
                left="0",
                width="100vw",
                height="100vh",
                z_index="25",
                background="transparent",
                on_click=State.close_notifications,
            ),
            rx.box(),
        ),
        rx.button(
            rx.icon("bell", size=18),
            variant="ghost",
            size="2",
            on_click=State.toggle_notifications,
            padding="0",
            width="40px",
            height="40px",
            border_radius="12px",
            border="1px solid #e5e7eb",
            background="white",
            color="#0f172a",
            _hover={"background": "rgba(148, 163, 184, 0.12)"},
        ),
        rx.cond(
            State.unread_notifications > 0,
            rx.box(
                rx.text(
                    rx.cond(
                        State.unread_notifications > 9,
                        "9+",
                        State.unread_notifications,
                    ),
                    font_size="9px",
                    color="white",
                    font_weight="600",
                ),
                min_width="16px",
                height="16px",
                border_radius="999px",
                background="#22c55e",
                border="2px solid white",
                position="absolute",
                top="-2px",
                right="-2px",
                display="flex",
                align_items="center",
                justify_content="center",
                padding="0 4px",
                pointer_events="none",
            ),
            rx.box(),
        ),
        rx.cond(State.notifications_open, notifications_panel(), rx.box()),
        position="relative",
    )


def search_result_item(result: dict) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.vstack(
                rx.text(result["nombre"], font_size="13px", font_weight="500"),
                rx.hstack(
                    rx.text(result["cedis"], font_size="11px", color="#94a3b8"),
                    rx.text("-", font_size="11px", color="#cbd5e1"),
                    rx.text(result["gobierno"], font_size="11px", color="#94a3b8"),
                    spacing="1",
                    align="center",
                ),
                spacing="1",
                align="start",
            ),
            rx.text(result["numero"], font_size="11px", color="#64748b"),
            justify="between",
            align="center",
            width="100%",
            padding="8px 10px",
            border_radius="10px",
            _hover={"background": "rgba(148, 163, 184, 0.14)"},
        ),
        href="/",
        underline="none",
        width="100%",
        on_click=State.select_search_result(result["cedis"], result["id"]),
    )


def search_results_panel() -> rx.Component:
    return rx.cond(
        State.show_search_results,
        rx.box(
            rx.cond(
                State.has_search_results,
                rx.vstack(
                    rx.foreach(State.search_results, search_result_item),
                    spacing="1",
                    width="100%",
                ),
                rx.text(
                    "Sin resultados",
                    font_size="12px",
                    color="#94a3b8",
                    padding="8px 10px",
                ),
            ),
            position="absolute",
            top="calc(100% + 6px)",
            left="0",
            right="0",
            padding="6px",
            background="white",
            border="1px solid #e5e7eb",
            border_radius="12px",
            box_shadow="0 12px 28px rgba(15, 23, 42, 0.12)",
            width="100%",
            z_index="20",
        ),
        rx.box(),
    )


def top_header() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            notification_bell(),
            rx.hstack(
                rx.avatar(name=State.current_user_name, size="4", color_scheme="blue"),
                rx.vstack(
                    rx.text(State.current_user_name, font_weight="600", font_size="14px"),
                    rx.text("Usuario", font_size="12px", color="#64748b"),
                    spacing="0",
                    align="start",
                ),
                rx.cond(
                    State.is_authenticated,
                    rx.button(
                        rx.icon("log-out", size=14),
                        variant="ghost",
                        size="1",
                        on_click=State.logout,
                    ),
                    rx.box(),
                ),
                spacing="3",
                align="center",
            ),
            spacing="4",
            align="center",
        ),
        justify="end",
        align="center",
        width="100%",
        padding="20px 28px 15px 28px",
    )
