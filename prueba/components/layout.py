"""Diseño de página compartido."""

import reflex as rx

from ..pages.login import login_page
from ..state import State
from .header import top_header
from .sidebar import sidebar


def page_shell(content: rx.Component, *, header_overlap: bool = True) -> rx.Component:
    return rx.cond(
        State.is_authenticated,
        rx.flex(
            sidebar(),
            rx.box(
                top_header(),
                rx.box(
                    content,
                    width="100%",
                    padding_top="0px",
                    margin_top="-50px" if header_overlap else "0px",
                    overflow="visible",
                ),
                background="rgba(248, 250, 252, 0.6)",
                backdrop_filter="blur(16px)",
                border_left="1px solid rgba(255, 255, 255, 0.6)",
                flex="1",
                min_width="0",
                min_height="100vh",
                overflow="visible",
            ),
            width="100%",
            min_height="100vh",
            overflow="visible",
            background=(
                "radial-gradient(circle at 12% 6%, rgba(255, 255, 255, 0.9) 0%, "
                "rgba(226, 232, 240, 0.85) 45%, rgba(226, 232, 240, 0.75) 100%), "
                "linear-gradient(135deg, rgba(248, 250, 252, 0.95), "
                "rgba(226, 232, 240, 0.9))"
            ),
        ),
        login_page(),
    )
