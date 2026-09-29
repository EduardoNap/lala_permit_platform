"""Punto de entrada de la app Reflex."""

import reflex as rx

from .pages.about import about_page
from .pages.cedis import cedis_page
from .pages.dashboard import dashboard_page
from .pages.historial import historial_page
from .pages.login import login_page
from .pages.permits import permits_page
from .pages.regiones import regiones_page
from .pages.upload_permit import upload_permit_page
from .state import State
from .theme import BASE_STYLE, STYLESHEETS


FAVICON_META = [
    rx.el.link(rel="icon", href="/company-logo.png?v=1", type="image/png"),
    rx.el.link(rel="shortcut icon", href="/company-logo.png?v=1", type="image/png"),
]


app = rx.App(style=BASE_STYLE, stylesheets=STYLESHEETS, theme=rx.theme(appearance="light"))
app.add_page(
    login_page,
    route="/login",
    on_load=State.load_auth_state,
    image="/company-logo.png",
    meta=FAVICON_META,
)
app.add_page(
    dashboard_page,
    route="/",
    on_load=State.set_active_page("dashboard"),
    image="/company-logo.png",
    meta=FAVICON_META,
)
app.add_page(
    regiones_page,
    route="/regiones",
    on_load=State.set_active_page("regiones"),
    image="/company-logo.png",
    meta=FAVICON_META,
)
app.add_page(
    cedis_page,
    route="/cedis",
    on_load=State.set_active_page("regiones"),
    image="/company-logo.png",
    meta=FAVICON_META,
)
app.add_page(
    upload_permit_page,
    route="/cargar-permiso",
    on_load=State.set_active_page("cargar-permiso"),
    image="/company-logo.png",
    meta=FAVICON_META,
)
app.add_page(
    permits_page,
    route="/tareas",
    on_load=State.set_active_page("tareas"),
    image="/company-logo.png",
    meta=FAVICON_META,
)
app.add_page(
    historial_page,
    route="/historial",
    on_load=State.set_active_page("historial"),
    image="/company-logo.png",
    meta=FAVICON_META,
)
app.add_page(
    about_page,
    route="/acerca",
    on_load=State.set_active_page("about"),
    image="/company-logo.png",
    meta=FAVICON_META,
)
