"""Diseño de página para cargar permisos."""

import reflex as rx

from ..components.layout import page_shell
from ..state import State


def field_label(text: str, required: bool = False) -> rx.Component:
    return rx.hstack(
        rx.text(text, font_size="12px", color="#64748b"),
        rx.cond(required, rx.text("*", font_size="12px", color="#dc2626"), rx.box()),
        spacing="1",
        align="center",
    )


def text_field(label: str, placeholder: str, required: bool = False) -> rx.Component:
    return rx.vstack(
        field_label(label, required),
        rx.input(
            placeholder=placeholder,
            background="white",
            border="1px solid #e2e8f0",
            border_radius="10px",
        ),
        spacing="2",
        width="100%",
    )


def select_field(label: str, options: list[str], required: bool = False) -> rx.Component:
    return rx.vstack(
        field_label(label, required),
        rx.select(
            options,
            background="white",
            border="1px solid #e2e8f0",
            border_radius="10px",
        ),
        spacing="2",
        width="100%",
    )


def _scope_button(label: str, value: str) -> rx.Component:
    is_active = State.upload_permit_scope == value
    is_locked = (State.upload_fields_pdf != "") | State.upload_extract_loading
    return rx.button(
        label,
        size="1",
        on_click=State.set_upload_permit_scope(value),
        border_radius="999px",
        padding="6px 14px",
        background=rx.cond(is_active, "#2563eb", "transparent"),
        color=rx.cond(is_active, "white", "#475569"),
        border="1px solid transparent",
        disabled=is_locked,
        _hover={
            "background": "rgba(37, 99, 235, 0.12)",
            "color": "#1e293b",
        },
    )


def permit_scope_toggle() -> rx.Component:
    return rx.hstack(
        _scope_button("N/A", ""),
        _scope_button("Municipal", "Municipal"),
        _scope_button("Estatal", "Estatal"),
        _scope_button("Federal", "Federal"),
        spacing="1",
        padding="4px",
        border_radius="999px",
        border="1px solid #e2e8f0",
        background="rgba(15, 23, 42, 0.04)",
    )


def upload_loading_indicator() -> rx.Component:
    return rx.cond(
        State.upload_is_busy | State.upload_extract_loading,
        rx.hstack(
            rx.spinner(size="3", color="#1d4ed8"),
            rx.text("Cargando...", font_size="11px", color="#1d4ed8"),
            spacing="1",
            align="center",
            padding="4px 8px",
            border_radius="999px",
            background="rgba(37, 99, 235, 0.12)",
            border="1px solid rgba(37, 99, 235, 0.3)",
        ),
        rx.box(width="36px", height="18px"),
    )


def pdf_preview(
    file_key: rx.Var,
    file_url: rx.Var,
    title: str,
    description: str,
    height: str = "360px",
) -> rx.Component:
    return rx.box(
        rx.cond(
            file_key != "",
            rx.el.iframe(
                src=file_url,
                width="100%",
                height="100%",
                style={"border": "none"},
            ),
            rx.vstack(
                rx.text(title, font_size="14px", font_weight="600", color="#64748b"),
                rx.text(description, font_size="12px", color="#94a3b8"),
                spacing="2",
                align="center",
                justify="center",
                height="100%",
            ),
        ),
        height=height,
        border="1px solid #e2e8f0",
        border_radius="12px",
        background="linear-gradient(180deg, #f8fafc, #eef2ff)",
        width="100%",
        overflow="hidden",
    )


def pdf_page_with_highlights(page: rx.Var) -> rx.Component:
    return rx.box(
        rx.image(
            src=rx.get_upload_url(page["file"]),
            width="100%",
            display="block",
        ),
        rx.foreach(
            State.upload_highlight_boxes,
            lambda box: rx.cond(
                box["page"] == page["page"],
                rx.box(
                    position="absolute",
                    left=box["left"],
                    top=box["top"],
                    width=box["width"],
                    height=box["height"],
                    border="2px solid #f59e0b",
                    background="rgba(245, 158, 11, 0.2)",
                    box_shadow="0 0 0 1px rgba(245, 158, 11, 0.3)",
                    pointer_events="none",
                ),
                rx.box(),
            ),
        ),
        id=page["id"],
        position="relative",
        width="100%",
        border="1px solid #e2e8f0",
        border_radius="10px",
        overflow="hidden",
        background="white",
    )


def pdf_preview_with_highlights(
    pages: rx.Var,
    has_pages: rx.Var,
    file_key: rx.Var,
    file_url: rx.Var,
    title: str,
    description: str,
    height: str = "480px",
) -> rx.Component:
    return rx.box(
        rx.cond(
            has_pages,
            rx.box(
                rx.vstack(
                    rx.foreach(pages, pdf_page_with_highlights),
                    spacing="4",
                    width="100%",
                ),
                max_height=height,
                overflow="auto",
                width="100%",
            ),
            rx.cond(
                file_key != "",
                rx.el.iframe(
                    src=file_url,
                    width="100%",
                    height="100%",
                    style={"border": "none"},
                ),
                rx.vstack(
                    rx.text(title, font_size="14px", font_weight="600", color="#64748b"),
                    rx.text(description, font_size="12px", color="#94a3b8"),
                    spacing="2",
                    align="center",
                    justify="center",
                    height="100%",
                ),
            ),
        ),
        height=height,
        border="1px solid #e2e8f0",
        border_radius="12px",
        background="linear-gradient(180deg, #f8fafc, #eef2ff)",
        width="100%",
        overflow="hidden",
    )


def _step_pill(label: str, is_active: rx.Var, is_done: rx.Var) -> rx.Component:
    is_highlight = is_active | is_done
    return rx.hstack(
        rx.text(
            label,
            font_size="12px",
            font_weight=rx.cond(is_active, "600", "500"),
            color=rx.cond(is_highlight, "#166534", "#64748b"),
        ),
        align="center",
        padding="6px 14px",
        border_radius="999px",
        border=rx.cond(
            is_highlight,
            "2px solid rgba(22, 163, 74, 0.45)",
            "2px solid rgba(148, 163, 184, 0.35)",
        ),
        background=rx.cond(
            is_highlight,
            "rgba(22, 163, 74, 0.12)",
            "rgba(148, 163, 184, 0.12)",
        ),
        min_width="140px",
        justify="center",
    )


def _step_connector(active: rx.Var) -> rx.Component:
    return rx.box(
        height="6px",
        flex="1",
        background=rx.cond(active, "#16a34a", "#e2e8f0"),
        border_radius="999px",
    )


def upload_steps_bar() -> rx.Component:
    primary_done = State.upload_primary_pdf != ""
    secondary_done = State.upload_secondary_pdf != ""
    fields_done = State.upload_fields_pdf != ""
    extra_done = State.upload_extra_pdf != ""
    primary_active = State.upload_step == 1
    secondary_active = State.upload_step == 2
    fields_active = State.upload_step == 3
    extra_active = State.upload_step == 4

    base_bar = rx.hstack(
        _step_pill("Acuse", primary_active, primary_done),
        _step_connector(primary_done),
        _step_pill("Pago", secondary_active, secondary_done),
        _step_connector(secondary_done),
        _step_pill("Permiso", fields_active, fields_done),
        spacing="2",
        align="center",
        width="100%",
    )

    after_one = rx.hstack(
        _step_pill("Acuse", primary_active, primary_done),
        _step_connector(primary_done),
        _step_pill("Archivo extra", extra_active, extra_done),
        _step_connector(extra_done),
        _step_pill("Pago", secondary_active, secondary_done),
        _step_connector(secondary_done),
        _step_pill("Permiso", fields_active, fields_done),
        spacing="2",
        align="center",
        width="100%",
    )

    after_two = rx.hstack(
        _step_pill("Acuse", primary_active, primary_done),
        _step_connector(primary_done),
        _step_pill("Pago", secondary_active, secondary_done),
        _step_connector(secondary_done),
        _step_pill("Archivo extra", extra_active, extra_done),
        _step_connector(extra_done),
        _step_pill("Permiso", fields_active, fields_done),
        spacing="2",
        align="center",
        width="100%",
    )

    after_three = rx.hstack(
        _step_pill("Acuse", primary_active, primary_done),
        _step_connector(primary_done),
        _step_pill("Pago", secondary_active, secondary_done),
        _step_connector(secondary_done),
        _step_pill("Permiso", fields_active, fields_done),
        _step_connector(fields_done),
        _step_pill("Archivo extra", extra_active, extra_done),
        spacing="2",
        align="center",
        width="100%",
    )

    return rx.cond(
        State.show_upload_extra_step,
        rx.cond(
            State.upload_extra_after_step == 1,
            after_one,
            rx.cond(
                State.upload_extra_after_step == 2,
                after_two,
                rx.cond(State.upload_extra_after_step == 3, after_three, base_bar),
            ),
        ),
        base_bar,
    )


def permit_fields_municipal() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            field_label("CEDIS", True),
            rx.select(
                State.cedis_locations,
                value=State.upload_cedis,
                on_change=State.set_upload_cedis,
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Fecha de emisión", True),
            rx.input(
                type="date",
                value=State.upload_fecha_emision,
                on_change=State.set_upload_fecha_emision,
                on_click=State.select_upload_field("fecha_emision"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Vigencia", True),
            rx.input(
                type="date",
                value=State.upload_vigencia,
                on_change=State.set_upload_vigencia,
                on_click=State.select_upload_field("vigencia"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Nombre", True),
            rx.input(
                placeholder="Permiso municipal",
                value=State.upload_nombre,
                on_change=State.set_upload_nombre,
                on_click=State.select_upload_field("nombre"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Registro", True),
            rx.input(
                placeholder="Folio / Número / Autorización",
                value=State.upload_registro,
                on_change=State.set_upload_registro,
                on_click=State.select_upload_field("registro"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Condicionantes"),
            rx.vstack(
                rx.foreach(
                    State.upload_condicionantes_items,
                    lambda item: rx.hstack(
                        rx.box(
                            rx.text(
                                item["label"],
                                font_size="10px",
                                font_weight="600",
                                color="#475569",
                            ),
                            background="rgba(148, 163, 184, 0.2)",
                            border_radius="999px",
                            padding="2px 6px",
                            min_width="24px",
                            text_align="center",
                        ),
                        rx.text_area(
                            placeholder="Condicionante",
                            value=item["text"],
                            on_change=State.set_upload_condicionante_item(
                                item["index"]
                            ),
                            on_click=State.select_upload_field("condicionantes"),
                            auto_height=True,
                            rows="2",
                            resize="none",
                            min_height="60px",
                            background="white",
                            border="1px solid #e2e8f0",
                            border_radius="10px",
                            width="100%",
                        ),
                        rx.button(
                            rx.icon("trash-2", size=14),
                            variant="ghost",
                            size="1",
                            color="#b91c1c",
                            _hover={"background": "rgba(185, 28, 28, 0.08)"},
                            on_click=State.remove_upload_condicionante(item["index"]),
                        ),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                ),
                rx.button(
                    "Agregar condicionante",
                    variant="soft",
                    size="1",
                    on_click=State.add_upload_condicionante,
                ),
                spacing="1",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def permit_fields_estatal() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            field_label("CEDIS", True),
            rx.select(
                State.cedis_locations,
                value=State.upload_cedis,
                on_change=State.set_upload_cedis,
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Fecha de emisión", True),
            rx.input(
                type="date",
                value=State.upload_fecha_emision,
                on_change=State.set_upload_fecha_emision,
                on_click=State.select_upload_field("fecha_emision"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Vigencia", True),
            rx.input(
                type="date",
                value=State.upload_vigencia,
                on_change=State.set_upload_vigencia,
                on_click=State.select_upload_field("vigencia"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Nombre", True),
            rx.input(
                placeholder="Permiso de operacion",
                value=State.upload_nombre,
                on_change=State.set_upload_nombre,
                on_click=State.select_upload_field("nombre"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Registro", True),
            rx.input(
                placeholder="Registro del permiso",
                value=State.upload_registro,
                on_change=State.set_upload_registro,
                on_click=State.select_upload_field("registro"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Número", True),
            rx.input(
                placeholder="65686409",
                value=State.upload_numero,
                on_change=State.set_upload_numero,
                on_click=State.select_upload_field("numero"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Gobierno", True),
            rx.input(
                placeholder="Estatal",
                value=State.upload_gobierno,
                on_change=State.set_upload_gobierno,
                on_click=State.select_upload_field("gobierno"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Condicionantes"),
            rx.vstack(
                rx.foreach(
                    State.upload_condicionantes_items,
                    lambda item: rx.hstack(
                        rx.box(
                            rx.text(
                                item["label"],
                                font_size="10px",
                                font_weight="600",
                                color="#475569",
                            ),
                            background="rgba(148, 163, 184, 0.2)",
                            border_radius="999px",
                            padding="2px 6px",
                            min_width="24px",
                            text_align="center",
                        ),
                        rx.text_area(
                            placeholder="Condicionante",
                            value=item["text"],
                            on_change=State.set_upload_condicionante_item(
                                item["index"]
                            ),
                            on_click=State.select_upload_field("condicionantes"),
                            auto_height=True,
                            rows="2",
                            resize="none",
                            min_height="60px",
                            background="white",
                            border="1px solid #e2e8f0",
                            border_radius="10px",
                            width="100%",
                        ),
                        rx.button(
                            rx.icon("trash-2", size=14),
                            variant="ghost",
                            size="1",
                            color="#b91c1c",
                            _hover={"background": "rgba(185, 28, 28, 0.08)"},
                            on_click=State.remove_upload_condicionante(item["index"]),
                        ),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                ),
                rx.button(
                    "Agregar condicionante",
                    variant="soft",
                    size="1",
                    on_click=State.add_upload_condicionante,
                ),
                spacing="1",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def permit_fields_federal() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            field_label("CEDIS", True),
            rx.select(
                State.cedis_locations,
                value=State.upload_cedis,
                on_change=State.set_upload_cedis,
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Nombre"),
            rx.input(
                placeholder="Permiso federal",
                value=State.upload_nombre,
                on_change=State.set_upload_nombre,
                on_click=State.select_upload_field("nombre"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Fecha de emisión", True),
            rx.input(
                type="date",
                value=State.upload_fecha_emision,
                on_change=State.set_upload_fecha_emision,
                on_click=State.select_upload_field("fecha_emision"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("NRA", True),
            rx.input(
                placeholder="NRA",
                value=State.upload_nra,
                on_change=State.set_upload_nra,
                on_click=State.select_upload_field("nra"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Bitácora", True),
            rx.input(
                placeholder="Bitácora",
                value=State.upload_bitacora,
                on_change=State.set_upload_bitacora,
                on_click=State.select_upload_field("bitacora"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            field_label("Gobierno", True),
            rx.input(
                placeholder="Autoridad federal",
                value=State.upload_gobierno,
                on_change=State.set_upload_gobierno,
                on_click=State.select_upload_field("gobierno"),
                background="white",
                border="1px solid #e2e8f0",
                border_radius="10px",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def permit_fields_by_scope() -> rx.Component:
    return rx.cond(
        State.upload_permit_scope == "",
        rx.box(
            rx.text(
                "Primero seleccione la autoridad antes de continuar.",
                font_size="13px",
                color="#94a3b8",
                text_align="center",
            ),
            padding="24px 12px",
            border_radius="12px",
            border="1px dashed #e2e8f0",
            background="rgba(148, 163, 184, 0.08)",
            width="100%",
        ),
        rx.cond(
            State.upload_permit_scope == "Federal",
            permit_fields_federal(),
            rx.cond(
                State.upload_permit_scope == "Municipal",
                permit_fields_municipal(),
                permit_fields_estatal(),
            ),
        ),
    )


def upload_step_one() -> rx.Component:
    return rx.card(
        rx.flex(
            rx.vstack(
                rx.hstack(
                    rx.badge(
                        "Paso 1",
                        color="#1d4ed8",
                        background="rgba(59, 130, 246, 0.12)",
                        font_size="11px",
                        border_radius="999px",
                    ),
                    rx.cond(
                        State.upload_primary_pdf != "",
                        rx.badge(
                            "PDF cargado",
                            color="#15803d",
                            background="rgba(22, 163, 74, 0.12)",
                            font_size="11px",
                            border_radius="999px",
                        ),
                        rx.badge(
                            "Sin PDF",
                            color="#64748b",
                            background="rgba(148, 163, 184, 0.2)",
                            font_size="11px",
                            border_radius="999px",
                        ),
                    ),
                    rx.spacer(),
                    upload_loading_indicator(),
                    spacing="2",
                    align="center",
                    width="100%",
                ),
                rx.text(
                    "Acuse de Solicitud",
                    font_size="18px",
                    font_weight="600",
                    color="#0f172a",
                ),
                rx.text(
                    "Guarda el acuse oficial antes de continuar con el proceso.",
                    font_size="12px",
                    color="#64748b",
                ),
                rx.box(
                    rx.vstack(
                        rx.text(
                            "Carga tu PDF",
                            font_size="13px",
                            font_weight="600",
                            color="#0f172a",
                        ),
                        rx.text(
                            "Usa el boton para seleccionar el acuse.",
                            font_size="12px",
                            color="#94a3b8",
                        ),
                        rx.upload(
                            rx.button(
                                rx.hstack(
                                    rx.icon("upload", size=16),
                                    rx.text("Subir acuse", font_size="13px"),
                                    spacing="2",
                                    align="center",
                                ),
                                color_scheme="blue",
                                size="2",
                            ),
                            on_drop=State.handle_primary_upload,
                            accept={"application/pdf": [".pdf"]},
                            multiple=False,
                        ),
                        spacing="2",
                        align="center",
                        width="100%",
                    ),
                    border="1px dashed #cbd5e1",
                    border_radius="12px",
                    background="rgba(226, 232, 240, 0.45)",
                    padding="14px",
                    width="100%",
                ),
                rx.cond(
                    State.upload_primary_pdf != "",
                    rx.hstack(
                        rx.icon("check", size=16, color="#16a34a"),
                        rx.text(
                            State.upload_primary_pdf_name,
                            font_size="12px",
                            color="#475569",
                            overflow_wrap="anywhere",
                        ),
                        spacing="2",
                        align="center",
                        width="100%",
                    ),
                    rx.box(),
                ),
                rx.vstack(
                    field_label("Comentarios"),
                    rx.text_area(
                        placeholder="Comentario del acuse",
                        value=State.upload_primary_pdf_comment,
                        on_change=State.set_upload_primary_pdf_comment,
                        auto_height=True,
                        rows="2",
                        resize="none",
                        min_height="60px",
                        background="white",
                        border="1px solid #e2e8f0",
                        border_radius="10px",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.cond(
                        State.upload_primary_pdf != "",
                        rx.link(
                            rx.button("Guardar", variant="soft", size="2"),
                            href="/cedis",
                            underline="none",
                            on_click=State.save_upload_step_pdf("primary"),
                        ),
                        rx.button(
                            "Guardar",
                            variant="soft",
                            size="2",
                            disabled=True,
                        ),
                    ),
                    rx.cond(
                        State.upload_extra_pdf == "",
                        rx.button(
                            "Archivo extra",
                            variant="soft",
                            size="2",
                            on_click=State.start_extra_step(1),
                            disabled=rx.cond(
                                State.upload_primary_pdf != "", False, True
                            ),
                        ),
                        rx.box(),
                    ),
                    rx.button(
                        rx.hstack(
                            rx.text("Continuar", font_size="13px"),
                            rx.icon("arrow-right", size=16),
                            spacing="2",
                            align="center",
                        ),
                        on_click=State.save_primary_and_continue,
                        color_scheme="blue",
                        size="2",
                        disabled=rx.cond(State.upload_primary_pdf != "", False, True),
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.cond(
                    State.upload_save_error != "",
                    rx.text(
                        State.upload_save_error,
                        font_size="12px",
                        color="#b91c1c",
                    ),
                    rx.box(),
                ),
                rx.cond(
                    State.upload_save_success != "",
                    rx.text(
                        State.upload_save_success,
                        font_size="12px",
                        color="#15803d",
                    ),
                    rx.box(),
                ),
                spacing="3",
                flex="1",
                min_width="0",
                width="100%",
            ),
            rx.box(
                pdf_preview(
                    State.upload_primary_pdf,
                    rx.cond(
                        State.use_s3,
                        State.upload_primary_pdf_url,
                        rx.get_upload_url(State.upload_primary_pdf),
                    ),
                    "Vista previa del acuse",
                    "Sube el PDF para ver el documento aqui.",
                    height="490px",
                ),
                width="100%",
                flex="1",
                min_width="0",
            ),
            direction={"base": "column", "lg": "row"},
            gap="16px",
            width="100%",
        ),
        padding="18px",
        border_radius="16px",
        border="1px solid #e5e7eb",
        box_shadow="0 10px 24px rgba(15, 23, 42, 0.06)",
        background="white",
        width="100%",
    )


def upload_step_two() -> rx.Component:
    return rx.card(
        rx.flex(
            rx.vstack(
                rx.hstack(
                    rx.badge(
                        "Paso 2",
                        color="#1d4ed8",
                        background="rgba(59, 130, 246, 0.12)",
                        font_size="11px",
                        border_radius="999px",
                    ),
                    rx.cond(
                        State.upload_secondary_pdf != "",
                        rx.badge(
                            "PDF cargado",
                            color="#15803d",
                            background="rgba(22, 163, 74, 0.12)",
                            font_size="11px",
                            border_radius="999px",
                        ),
                        rx.badge(
                            "Sin PDF",
                            color="#64748b",
                            background="rgba(148, 163, 184, 0.2)",
                            font_size="11px",
                            border_radius="999px",
                        ),
                    ),
                    rx.spacer(),
                    upload_loading_indicator(),
                    spacing="2",
                    align="center",
                    width="100%",
                ),
                rx.text(
                    "Pago de Derechos",
                    font_size="18px",
                    font_weight="600",
                    color="#0f172a",
                ),
                rx.text(
                    "Adjunta el comprobante para validar el trámite.",
                    font_size="12px",
                    color="#64748b",
                ),
                rx.box(
                    rx.vstack(
                        rx.text(
                            "Carga tu PDF",
                            font_size="13px",
                            font_weight="600",
                            color="#0f172a",
                        ),
                        rx.text(
                            "Sube el comprobante de pago de derechos.",
                            font_size="12px",
                            color="#94a3b8",
                        ),
                        rx.upload(
                            rx.button(
                                rx.hstack(
                                    rx.icon("upload", size=16),
                                    rx.text("Subir pago", font_size="13px"),
                                    spacing="2",
                                    align="center",
                                ),
                                color_scheme="blue",
                                size="2",
                            ),
                            on_drop=State.handle_secondary_upload,
                            accept={"application/pdf": [".pdf"]},
                            multiple=False,
                        ),
                        spacing="2",
                        align="center",
                        width="100%",
                    ),
                    border="1px dashed #cbd5e1",
                    border_radius="12px",
                    background="rgba(226, 232, 240, 0.45)",
                    padding="14px",
                    width="100%",
                ),
                rx.cond(
                    State.upload_secondary_pdf != "",
                    rx.hstack(
                        rx.icon("check", size=16, color="#16a34a"),
                        rx.text(
                            State.upload_secondary_pdf_name,
                            font_size="12px",
                            color="#475569",
                            overflow_wrap="anywhere",
                        ),
                        spacing="2",
                        align="center",
                        width="100%",
                    ),
                    rx.box(),
                ),
                rx.vstack(
                    field_label("Comentarios"),
                    rx.text_area(
                        placeholder="Comentario del pago de derechos",
                        value=State.upload_secondary_pdf_comment,
                        on_change=State.set_upload_secondary_pdf_comment,
                        auto_height=True,
                        rows="2",
                        resize="none",
                        min_height="60px",
                        background="white",
                        border="1px solid #e2e8f0",
                        border_radius="10px",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        rx.hstack(
                            rx.icon("arrow-left", size=16),
                            rx.text("Regresar", font_size="13px"),
                            spacing="2",
                            align="center",
                        ),
                        on_click=State.show_upload_step_two_back,
                        variant="soft",
                        size="2",
                    ),
                    rx.spacer(),
                    rx.cond(
                        State.upload_secondary_pdf != "",
                        rx.link(
                            rx.button("Guardar", variant="soft", size="2"),
                            href="/cedis",
                            underline="none",
                            on_click=State.save_upload_step_pdf("secondary"),
                        ),
                        rx.button(
                            "Guardar",
                            variant="soft",
                            size="2",
                            disabled=True,
                        ),
                    ),
                    rx.cond(
                        State.upload_extra_pdf == "",
                        rx.button(
                            "Archivo extra",
                            variant="soft",
                            size="2",
                            on_click=State.start_extra_step(2),
                            disabled=rx.cond(
                                State.upload_secondary_pdf != "", False, True
                            ),
                        ),
                        rx.box(),
                    ),
                    rx.button(
                        rx.hstack(
                            rx.text("Continuar", font_size="13px"),
                            rx.icon("arrow-right", size=16),
                            spacing="2",
                            align="center",
                        ),
                        on_click=State.save_secondary_and_continue,
                        color_scheme="blue",
                        size="2",
                        disabled=rx.cond(State.upload_secondary_pdf != "", False, True),
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.cond(
                    State.upload_save_error != "",
                    rx.text(
                        State.upload_save_error,
                        font_size="12px",
                        color="#b91c1c",
                    ),
                    rx.box(),
                ),
                rx.cond(
                    State.upload_save_success != "",
                    rx.text(
                        State.upload_save_success,
                        font_size="12px",
                        color="#15803d",
                    ),
                    rx.box(),
                ),
                spacing="3",
                flex="1",
                min_width="0",
                width="100%",
            ),
            rx.box(
                pdf_preview(
                    State.upload_secondary_pdf,
                    rx.cond(
                        State.use_s3,
                        State.upload_secondary_pdf_url,
                        rx.get_upload_url(State.upload_secondary_pdf),
                    ),
                    "Vista previa del pago",
                    "Sube el PDF para ver el documento aqui.",
                    height="490px",
                ),
                width="100%",
                flex="1",
                min_width="0",
            ),
            direction={"base": "column", "lg": "row"},
            gap="16px",
            width="100%",
        ),
        padding="18px",
        border_radius="16px",
        border="1px solid #e5e7eb",
        box_shadow="0 10px 24px rgba(15, 23, 42, 0.06)",
        background="white",
        width="100%",
    )


def upload_step_three() -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.card(
                rx.vstack(
                    rx.flex(
                        rx.text("Campos del Permiso", font_size="16px", font_weight="600"),
                        rx.hstack(
                            permit_scope_toggle(),
                            upload_loading_indicator(),
                            spacing="2",
                            align="center",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                        direction={"base": "column", "md": "row"},
                        gap="8px",
                    ),
                    permit_fields_by_scope(),
                    spacing="4",
                    width="100%",
                ),
                padding="20px",
                border_radius="12px",
                border="1px solid #e5e7eb",
                box_shadow="0 14px 30px rgba(15, 23, 42, 0.08)",
                background="white",
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text(
                                "PDF del permiso",
                                font_size="15px",
                                font_weight="600",
                                color="#0f172a",
                            ),
                            rx.text(
                                "Documento principal para extraer los campos.",
                                font_size="12px",
                                color="#94a3b8",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.hstack(
                            rx.hstack(
                                rx.text(
                                    "Usar extracción automática",
                                    font_size="12px",
                                    color="#64748b",
                                ),
                                rx.switch(
                                    checked=State.upload_use_extraction,
                                    on_change=State.set_upload_use_extraction,
                                    size="2",
                                    color_scheme="blue",
                                ),
                                spacing="2",
                                align="center",
                            ),
                            rx.cond(
                                State.upload_fields_pdf != "",
                                rx.badge(
                                    "PDF cargado",
                                    color="#15803d",
                                    background="rgba(22, 163, 74, 0.12)",
                                    font_size="11px",
                                    border_radius="999px",
                                ),
                                rx.badge(
                                    "Pendiente",
                                    color="#64748b",
                                    background="rgba(148, 163, 184, 0.2)",
                                    font_size="11px",
                                    border_radius="999px",
                                ),
                            ),
                            spacing="3",
                            align="center",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                    ),
                    pdf_preview_with_highlights(
                        State.upload_fields_pages,
                        State.upload_fields_has_pages,
                        State.upload_fields_pdf,
                        rx.cond(
                            State.use_s3,
                            State.upload_fields_pdf_url,
                            rx.get_upload_url(State.upload_fields_pdf),
                        ),
                        "Vista previa del permiso",
                        "Sube un PDF para renderizar el documento aqui.",
                        height="480px",
                    ),
                    rx.vstack(
                        field_label("Comentarios"),
                        rx.text_area(
                            placeholder="Comentario del permiso",
                            value=State.upload_fields_pdf_comment,
                            on_change=State.set_upload_fields_pdf_comment,
                            auto_height=True,
                            rows="2",
                            resize="none",
                            min_height="60px",
                            background="white",
                            border="1px solid #e2e8f0",
                            border_radius="10px",
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("file-text", size=16, color="#1f3a5f"),
                                rx.text(
                                    "Archivo PDF",
                                    font_size="12px",
                                    color="#64748b",
                                ),
                                spacing="2",
                                align="center",
                            ),
                            rx.text(
                                "Selecciona el documento principal del permiso.",
                                font_size="12px",
                                color="#94a3b8",
                            ),
                            rx.cond(
                                State.upload_permit_scope == "",
                                rx.button(
                                    rx.hstack(
                                        rx.icon("upload", size=16),
                                        rx.text("Subir PDF", font_size="13px"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    color_scheme="blue",
                                    size="2",
                                    disabled=True,
                                ),
                                rx.upload(
                                    rx.button(
                                        rx.hstack(
                                            rx.icon("upload", size=16),
                                            rx.text("Subir PDF", font_size="13px"),
                                            spacing="2",
                                            align="center",
                                        ),
                                        color_scheme="blue",
                                        size="2",
                                    ),
                                    on_drop=State.handle_fields_upload,
                                    accept={"application/pdf": [".pdf"]},
                                    multiple=False,
                                ),
                            ),
                            rx.cond(
                                State.upload_permit_scope == "",
                                rx.text(
                                    "Selecciona la autoridad antes de subir el PDF.",
                                    font_size="12px",
                                    color="#b91c1c",
                                ),
                                rx.box(),
                            ),
                            spacing="2",
                            align="center",
                            width="100%",
                        ),
                        border="1px dashed #cbd5e1",
                        border_radius="12px",
                        background="rgba(226, 232, 240, 0.45)",
                        padding="14px",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button(
                            rx.hstack(
                                rx.icon("arrow-left", size=16),
                                rx.text("Regresar", font_size="13px"),
                                spacing="2",
                                align="center",
                            ),
                            on_click=State.show_upload_step_three_back,
                            variant="soft",
                            size="2",
                        ),
                        rx.spacer(),
                        rx.cond(
                            State.upload_extra_pdf == "",
                            rx.button(
                                "Archivo extra",
                                variant="soft",
                                size="2",
                                on_click=State.start_extra_step(2),
                                disabled=rx.cond(
                                    State.upload_secondary_pdf != "", False, True
                                ),
                            ),
                            rx.box(),
                        ),
                        rx.cond(
                            State.can_save_permit,
                            rx.link(
                                rx.button(
                                    "Guardar",
                                    color_scheme="blue",
                                    size="2",
                                ),
                                href="/cedis",
                                underline="none",
                                on_click=State.update_current_permit,
                            ),
                            rx.button(
                                "Guardar",
                                color_scheme="blue",
                                size="2",
                                disabled=True,
                            ),
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.text(
                        State.upload_pdfs_label,
                        font_size="12px",
                        color="#64748b",
                    ),
                    rx.cond(
                        State.upload_use_extraction,
                        rx.cond(
                            State.upload_extract_loading,
                            rx.text(
                                "Extrayendo campos del PDF...",
                                font_size="12px",
                                color="#64748b",
                            ),
                            rx.cond(
                                State.upload_extract_error != "",
                                rx.text(
                                    State.upload_extract_error,
                                    font_size="12px",
                                    color="#b91c1c",
                                ),
                                rx.cond(
                                    State.upload_extract_status != "",
                                    rx.text(
                                        State.upload_extract_status,
                                        font_size="12px",
                                        color="#15803d",
                                    ),
                                    rx.box(),
                                ),
                            ),
                        ),
                        rx.text(
                            "Extracción automática desactivada.",
                            font_size="12px",
                            color="#94a3b8",
                        ),
                    ),
                    rx.cond(
                        State.upload_save_error != "",
                        rx.text(
                            State.upload_save_error,
                            font_size="12px",
                            color="#b91c1c",
                        ),
                        rx.box(),
                    ),
                    rx.cond(
                        State.upload_save_success != "",
                        rx.text(
                            State.upload_save_success,
                            font_size="12px",
                            color="#15803d",
                        ),
                        rx.box(),
                    ),
                    spacing="3",
                    width="100%",
                ),
                padding="18px",
                border_radius="16px",
                border="1px solid #e5e7eb",
                box_shadow="0 10px 24px rgba(15, 23, 42, 0.06)",
                background="white",
                width="100%",
            ),
            direction={"base": "column", "xl": "row"},
            gap="16px",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def upload_step_extra() -> rx.Component:
    continue_disabled = rx.cond(
        State.upload_extra_after_step == 1,
        State.upload_primary_pdf == "",
        rx.cond(
            State.upload_extra_after_step == 2,
            State.upload_secondary_pdf == "",
            True,
        ),
    )
    return rx.card(
        rx.flex(
            rx.vstack(
                rx.hstack(
                    rx.badge(
                        "Archivo extra",
                        color="#166534",
                        background="rgba(22, 163, 74, 0.12)",
                        font_size="11px",
                        border_radius="999px",
                    ),
                    rx.cond(
                        State.upload_extra_pdf != "",
                        rx.badge(
                            "PDF cargado",
                            color="#15803d",
                            background="rgba(22, 163, 74, 0.12)",
                            font_size="11px",
                            border_radius="999px",
                        ),
                        rx.badge(
                            "Sin PDF",
                            color="#64748b",
                            background="rgba(148, 163, 184, 0.2)",
                            font_size="11px",
                            border_radius="999px",
                        ),
                    ),
                    rx.spacer(),
                    upload_loading_indicator(),
                    spacing="2",
                    align="center",
                    width="100%",
                ),
                rx.text(
                    "Adjunta un archivo adicional para el trámite.",
                    font_size="13px",
                    color="#475569",
                ),
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("file-text", size=16, color="#1f3a5f"),
                            rx.text(
                                "Archivo PDF",
                                font_size="12px",
                                color="#64748b",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.text(
                            "Sube un documento extra para complementar el permiso.",
                            font_size="12px",
                            color="#94a3b8",
                        ),
                        rx.upload(
                            rx.button(
                                rx.hstack(
                                    rx.icon("upload", size=16),
                                    rx.text("Subir PDF", font_size="13px"),
                                    spacing="2",
                                    align="center",
                                ),
                                color_scheme="blue",
                                size="2",
                            ),
                            on_drop=State.handle_extra_upload,
                            accept={"application/pdf": [".pdf"]},
                            multiple=False,
                        ),
                        spacing="2",
                        align="center",
                        width="100%",
                    ),
                    border="1px dashed #cbd5e1",
                    border_radius="12px",
                    background="rgba(226, 232, 240, 0.45)",
                    padding="14px",
                    width="100%",
                ),
                rx.cond(
                    State.upload_extra_pdf != "",
                    rx.hstack(
                        rx.icon("check", size=16, color="#16a34a"),
                        rx.text(
                            State.upload_extra_pdf_name,
                            font_size="12px",
                            color="#475569",
                            overflow_wrap="anywhere",
                        ),
                        spacing="2",
                        align="center",
                        width="100%",
                    ),
                    rx.box(),
                ),
                rx.vstack(
                    field_label("Nombre del archivo"),
                    rx.input(
                        placeholder="Ej. Anexo tecnico",
                        value=State.upload_extra_pdf_label,
                        on_change=State.set_upload_extra_pdf_label,
                        background="white",
                        border="1px solid #e2e8f0",
                        border_radius="10px",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.vstack(
                    field_label("Comentarios"),
                    rx.text_area(
                        placeholder="Comentario del archivo extra",
                        value=State.upload_extra_pdf_comment,
                        on_change=State.set_upload_extra_pdf_comment,
                        auto_height=True,
                        rows="2",
                        resize="none",
                        min_height="60px",
                        background="white",
                        border="1px solid #e2e8f0",
                        border_radius="10px",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        rx.hstack(
                            rx.icon("arrow-left", size=16),
                            rx.text("Regresar", font_size="13px"),
                            spacing="2",
                            align="center",
                        ),
                        on_click=State.show_upload_extra_prev,
                        variant="soft",
                        size="2",
                    ),
                    rx.spacer(),
                    rx.cond(
                        State.upload_extra_pdf != "",
                        rx.link(
                            rx.button("Guardar", variant="soft", size="2"),
                            href="/cedis",
                            underline="none",
                            on_click=State.save_upload_extra_pdf,
                        ),
                        rx.button(
                            "Guardar",
                            variant="soft",
                            size="2",
                            disabled=True,
                        ),
                    ),
                    rx.button(
                        rx.hstack(
                            rx.text("Continuar", font_size="13px"),
                            rx.icon("arrow-right", size=16),
                            spacing="2",
                            align="center",
                        ),
                        on_click=State.show_upload_extra_next,
                        color_scheme="blue",
                        size="2",
                        disabled=continue_disabled,
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.cond(
                    State.upload_save_error != "",
                    rx.text(
                        State.upload_save_error,
                        font_size="12px",
                        color="#b91c1c",
                    ),
                    rx.box(),
                ),
                rx.cond(
                    State.upload_save_success != "",
                    rx.text(
                        State.upload_save_success,
                        font_size="12px",
                        color="#15803d",
                    ),
                    rx.box(),
                ),
                spacing="3",
                flex="1",
                min_width="0",
                width="100%",
            ),
            rx.box(
                pdf_preview(
                    State.upload_extra_pdf,
                    rx.cond(
                        State.use_s3,
                        State.upload_extra_pdf_url,
                        rx.get_upload_url(State.upload_extra_pdf),
                    ),
                    "Vista previa del archivo extra",
                    "Sube el PDF para ver el documento aqui.",
                    height="490px",
                ),
                width="100%",
                flex="1",
                min_width="0",
            ),
            direction={"base": "column", "lg": "row"},
            gap="16px",
            width="100%",
        ),
        padding="18px",
        border_radius="16px",
        border="1px solid #e5e7eb",
        box_shadow="0 10px 24px rgba(15, 23, 42, 0.06)",
        background="white",
        width="100%",
    )


def upload_permit_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.vstack(
                rx.text(
                    "Cargar nuevo permiso",
                    font_size="24px",
                    font_weight="600",
                ),
            ),
            rx.cond(
                State.upload_step == 3,
                rx.hstack(
                    rx.icon("info", size=16, color="#0284c7"),
                    rx.text(
                        "Verifica los resultados antes de usarlo.",
                        font_size="13px",
                        color="#0f172a",
                    ),
                    spacing="2",
                    align="center",
                    padding="10px 12px",
                    border_radius="10px",
                    border="1px solid #bae6fd",
                    background="rgba(14, 165, 233, 0.08)",
                    width="100%",
                ),
                rx.box(),
            ),
            upload_steps_bar(),
            rx.cond(
                State.upload_step == 1,
                upload_step_one(),
                rx.cond(
                    State.upload_step == 2,
                    upload_step_two(),
                    rx.cond(
                        State.upload_step == 3,
                        upload_step_three(),
                        upload_step_extra(),
                    ),
                ),
            ),
            spacing="4",
            width="100%",
        ),
        padding="0px 28px 32px 28px",
        width="100%",
    )


def upload_permit_page() -> rx.Component:
    return page_shell(upload_permit_content())

