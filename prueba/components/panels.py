"""Paneles grandes y de historial."""

import reflex as rx

from ..state import State


def current_sales_panel() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text("Ventas actuales", font_size="16px", font_weight="600"),
                rx.badge(
                    State.date_range,
                    color="#1f3a5f",
                    background="rgba(31, 58, 95, 0.12)",
                    font_size="12px",
                    border_radius="999px",
                ),
                justify="between",
                width="100%",
            ),
            rx.recharts.line_chart(
                rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke="#e2e8f0"),
                rx.recharts.line(
                    data_key="sales",
                    stroke="#1f3a5f",
                    stroke_width=3,
                    dot=False,
                ),
                rx.recharts.x_axis(data_key="day"),
                rx.recharts.y_axis(),
                rx.recharts.tooltip(),
                data=State.sales_over_time,
                width="100%",
                height=300,
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
        padding="18px",
        border_radius="12px",
        border="1px solid #e5e7eb",
        box_shadow="0 14px 30px rgba(15, 23, 42, 0.08)",
        background="white",
    )


def history_row(row: dict) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text(row["month"], font_weight="600", font_size="14px"),
            rx.text(
                f'{row["value"]:,} / {row["target"]:,}',
                font_size="12px",
                color="#64748b",
            ),
            justify="between",
            width="100%",
        ),
        rx.progress(
            value=row["percent"],
            max=100,
            height="8px",
            border_radius="999px",
            color_scheme="blue",
        ),
        spacing="2",
        width="100%",
    )


def history_panel() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text("Historial", font_size="16px", font_weight="600"),
                rx.text("Metas mensuales", font_size="12px", color="#64748b"),
                justify="between",
                width="100%",
            ),
            rx.vstack(
                rx.foreach(State.filtered_history, history_row),
                spacing="4",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
        padding="18px",
        border_radius="12px",
        border="1px solid #e5e7eb",
        box_shadow="0 14px 30px rgba(15, 23, 42, 0.08)",
        background="white",
    )
