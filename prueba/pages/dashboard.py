"""Diseño de página del tablero."""

import reflex as rx

from ..components.cedis_dashboard import (
    compliance_histogram_card,
    dashboard_kpi_strip,
    expiration_trend_card,
    permit_mix_card,
    permits_table_card,
    top_risk_cedis_card,
)
from ..components.layout import page_shell
from ..state import State


def dashboard_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(
                rx.cond(
                    State.current_user_name != "",
                    f"Bienvenido(a), {State.current_user_name}.",
                    "Bienvenido(a).",
                ),
                font_size="26px",
                font_weight="600",
                color="#0f172a",
            ),
            dashboard_kpi_strip(),
            rx.grid(
                expiration_trend_card(),
                permit_mix_card(),
                columns={"base": "1fr", "lg": "2fr 1fr"},
                gap="16px",
                width="100%",
            ),
            rx.grid(
                top_risk_cedis_card(),
                compliance_histogram_card(),
                columns={"base": "1fr", "lg": "1fr 1fr"},
                gap="16px",
                width="100%",
            ),
            permits_table_card(),
            spacing="4",
            width="100%",
        ),
        padding="0px 28px 32px 28px",
        width="100%",
    )


def dashboard_page() -> rx.Component:
    return page_shell(dashboard_content())
