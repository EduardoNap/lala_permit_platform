"""Tarjetas KPI y mini gráficas."""

import reflex as rx

from ..state import State


def delta_badge(delta: rx.Var, trend: rx.Var) -> rx.Component:
    return rx.cond(
        trend == "up",
        rx.badge(
            delta,
            color="#15803d",
            background="rgba(22, 163, 74, 0.12)",
            font_size="11px",
            border_radius="999px",
        ),
        rx.badge(
            delta,
            color="#b91c1c",
            background="rgba(239, 68, 68, 0.12)",
            font_size="11px",
            border_radius="999px",
        ),
    )


def kpi_card(title: rx.Var, value: rx.Var, delta: rx.Var, trend: rx.Var, chart: rx.Component) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(title, font_size="14px", color="#64748b"),
                rx.link(
                    "Ver",
                    href="#",
                    font_size="12px",
                    color="#1f3a5f",
                    underline="none",
                ),
                justify="between",
                width="100%",
            ),
            rx.hstack(
                rx.text(value, font_size="24px", font_weight="600"),
                delta_badge(delta, trend),
                spacing="3",
                align="center",
            ),
            rx.box(chart, width="100%", height="80px"),
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


def sales_kpi_card() -> rx.Component:
    return kpi_card(
        State.sales_title,
        State.sales_value,
        State.sales_delta,
        State.sales_trend,
        rx.recharts.line_chart(
            rx.recharts.line(
                data_key="sales",
                stroke="#1f3a5f",
                stroke_width=2,
                dot=False,
            ),
            rx.recharts.x_axis(data_key="day", hide=True),
            rx.recharts.y_axis(hide=True),
            rx.recharts.tooltip(),
            data=State.sales_over_time,
            width="100%",
            height=80,
        ),
    )


def visitors_kpi_card() -> rx.Component:
    return kpi_card(
        State.visitors_title,
        State.visitors_value,
        State.visitors_delta,
        State.visitors_trend,
        rx.recharts.bar_chart(
            rx.recharts.bar(
                data_key="visitors",
                fill="#38bdf8",
                radius=[6, 6, 0, 0],
            ),
            rx.recharts.x_axis(data_key="day", hide=True),
            rx.recharts.y_axis(hide=True),
            rx.recharts.tooltip(),
            data=State.visitors_over_time,
            width="100%",
            height=80,
        ),
    )


def repeat_kpi_card() -> rx.Component:
    return kpi_card(
        State.repeat_title,
        State.repeat_value,
        State.repeat_delta,
        State.repeat_trend,
        rx.recharts.area_chart(
            rx.recharts.area(
                data_key="new",
                stroke="#a855f7",
                fill="rgba(168, 85, 247, 0.25)",
                stroke_width=2,
            ),
            rx.recharts.area(
                data_key="repeat",
                stroke="#22c55e",
                fill="rgba(34, 197, 94, 0.25)",
                stroke_width=2,
            ),
            rx.recharts.x_axis(data_key="day", hide=True),
            rx.recharts.y_axis(hide=True),
            rx.recharts.tooltip(),
            data=State.customers_over_time,
            width="100%",
            height=80,
        ),
    )
