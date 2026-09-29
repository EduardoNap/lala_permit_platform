"""Bloques del tablero enfocados en CEDIS."""

import reflex as rx

from ..state import CONDITION_STATUS_LABELS, State


def info_row(label: str, value: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.text(
            label,
            font_size="12px",
            color="#64748b",
            max_width="45%",
            white_space="normal",
            overflow_wrap="anywhere",
        ),
        rx.text(
            value,
            font_size="13px",
            font_weight="500",
            max_width="55%",
            white_space="normal",
            overflow_wrap="anywhere",
            text_align="right",
        ),
        justify="between",
        align="start",
        wrap="wrap",
        width="100%",
    )


def status_badge(status: rx.Var) -> rx.Component:
    background = rx.cond(
        status == "Ingresado",
        "rgba(59, 130, 246, 0.16)",
        rx.cond(
            status == "Vigente",
            "rgba(22, 163, 74, 0.12)",
            rx.cond(
                status == "Por vencer",
                "rgba(245, 158, 11, 0.16)",
                "rgba(239, 68, 68, 0.12)",
            ),
        ),
    )
    color = rx.cond(
        status == "Ingresado",
        "#1d4ed8",
        rx.cond(
            status == "Vigente",
            "#15803d",
            rx.cond(status == "Por vencer", "#b45309", "#b91c1c"),
        ),
    )
    return rx.badge(
        status,
        color=color,
        background=background,
        font_size="11px",
        border_radius="999px",
        min_width="88px",
        justify_content="center",
        text_align="center",
        padding="4px 10px",
    )


def status_badge_large(status: rx.Var) -> rx.Component:
    background = rx.cond(
        status == "Ingresado",
        "rgba(59, 130, 246, 0.16)",
        rx.cond(
            status == "Vigente",
            "rgba(22, 163, 74, 0.12)",
            rx.cond(
                status == "Por vencer",
                "rgba(245, 158, 11, 0.16)",
                "rgba(239, 68, 68, 0.12)",
            ),
        ),
    )
    color = rx.cond(
        status == "Ingresado",
        "#1d4ed8",
        rx.cond(
            status == "Vigente",
            "#15803d",
            rx.cond(status == "Por vencer", "#b45309", "#b91c1c"),
        ),
    )
    return rx.badge(
        status,
        color=color,
        background=background,
        font_size="12px",
        border_radius="999px",
        min_width="96px",
        justify_content="center",
        text_align="center",
        padding="5px 12px",
    )


def permit_detail_value(value: rx.Var) -> rx.Var:
    return rx.cond(State.is_new_permit_selected, "", value)


def permit_detail_rows() -> rx.Component:
    return rx.cond(
        State.permit_scope == "Federal",
        rx.vstack(
            info_row("Nombre", permit_detail_value(State.permit_nombre)),
            info_row("NRA", permit_detail_value(State.permit_nra)),
            info_row("Bitácora", permit_detail_value(State.permit_bitacora)),
            info_row("Gobierno", permit_detail_value(State.permit_gobierno)),
            info_row(
                "Fecha de emisión", permit_detail_value(State.permit_fecha_emision)
            ),
            info_row("CEDIS", permit_detail_value(State.permit_cedis)),
            spacing="2",
            width="100%",
        ),
        rx.cond(
            State.permit_scope == "Municipal",
            rx.vstack(
                info_row("Nombre", permit_detail_value(State.permit_nombre)),
                info_row("Registro", permit_detail_value(State.permit_registro)),
                info_row(
                    "Fecha de emisión", permit_detail_value(State.permit_fecha_emision)
                ),
                info_row("Vigencia", permit_detail_value(State.permit_vigencia)),
                info_row("CEDIS", permit_detail_value(State.permit_cedis)),
                spacing="2",
                width="100%",
            ),
            rx.vstack(
                info_row("Nombre", permit_detail_value(State.permit_nombre)),
                info_row("Registro", permit_detail_value(State.permit_registro)),
                info_row(
                    "Fecha de emisión", permit_detail_value(State.permit_fecha_emision)
                ),
                info_row("Vigencia", permit_detail_value(State.permit_vigencia)),
                info_row("Gobierno", permit_detail_value(State.permit_gobierno)),
                info_row("Número", permit_detail_value(State.permit_numero)),
                info_row("CEDIS", permit_detail_value(State.permit_cedis)),
                spacing="2",
                width="100%",
            ),
        ),
    )


def _step_circle(status: str) -> rx.Component:
    if status == "done":
        color = "#22c55e"
        background = "rgba(34, 197, 94, 0.18)"
        border = "rgba(34, 197, 94, 0.35)"
        content = rx.icon("check", size=14, color=color)
    elif status == "active":
        color = "#60a5fa"
        background = "rgba(96, 165, 250, 0.18)"
        border = "rgba(96, 165, 250, 0.35)"
        content = rx.box(
            width="8px",
            height="8px",
            border_radius="999px",
            background=color,
        )
    else:
        color = "#94a3b8"
        background = "rgba(148, 163, 184, 0.15)"
        border = "rgba(148, 163, 184, 0.35)"
        content = rx.box(
            width="8px",
            height="8px",
            border_radius="999px",
            background=color,
        )
    return rx.box(
        content,
        width="28px",
        height="28px",
        border_radius="999px",
        border=f"2px solid {border}",
        background=background,
        display="flex",
        align_items="center",
        justify_content="center",
        flex_shrink="0",
    )


def _step_line(active: bool) -> rx.Component:
    return rx.box(
        height="2px",
        flex="1",
        background="#86efac" if active else "#e2e8f0",
        border_radius="999px",
    )


def permit_steps_bar() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            _step_circle("done"),
            rx.text("Datos", font_size="12px", color="#64748b"),
            spacing="1",
            align="center",
            min_width="90px",
        ),
        _step_line(True),
        rx.vstack(
            _step_circle("done"),
            rx.text("Documentos", font_size="12px", color="#64748b"),
            spacing="1",
            align="center",
            min_width="110px",
        ),
        _step_line(True),
        rx.vstack(
            _step_circle("active"),
            rx.text("Condicionantes", font_size="12px", color="#64748b"),
            spacing="1",
            align="center",
            min_width="130px",
        ),
        _step_line(False),
        rx.vstack(
            _step_circle("todo"),
            rx.text("Revisión", font_size="12px", color="#64748b"),
            spacing="1",
            align="center",
            min_width="90px",
        ),
        spacing="2",
        align="center",
        width="100%",
    )



def condition_status_select(item: rx.Var) -> rx.Component:
    status = item["status"]
    background = rx.cond(
        status == CONDITION_STATUS_LABELS["completado"],
        "rgba(22, 163, 74, 0.14)",
        rx.cond(
            status == CONDITION_STATUS_LABELS["en_proceso"],
            "rgba(245, 158, 11, 0.18)",
            "rgba(148, 163, 184, 0.18)",
        ),
    )
    color = rx.cond(
        status == CONDITION_STATUS_LABELS["completado"],
        "#15803d",
        rx.cond(
            status == CONDITION_STATUS_LABELS["en_proceso"],
            "#b45309",
            "#64748b",
        ),
    )
    options = [
        {
            "label": CONDITION_STATUS_LABELS["no_iniciado"],
            "color": "#64748b",
            "background": "rgba(148, 163, 184, 0.18)",
        },
        {
            "label": CONDITION_STATUS_LABELS["en_proceso"],
            "color": "#b45309",
            "background": "rgba(245, 158, 11, 0.18)",
        },
        {
            "label": CONDITION_STATUS_LABELS["completado"],
            "color": "#15803d",
            "background": "rgba(22, 163, 74, 0.14)",
        },
    ]
    return rx.el.select(
        *[
            rx.el.option(
                opt["label"],
                value=opt["label"],
                style={"color": opt["color"], "background": opt["background"]},
            )
            for opt in options
        ],
        value=status,
        on_change=State.set_condition_status(item["id"]),
        style={
            "background": background,
            "border": "1px solid #e2e8f0",
            "borderRadius": "999px",
            "color": color,
            "fontSize": "11px",
            "height": "28px",
            "minWidth": "140px",
            "padding": "0 8px",
            "outline": "none",
        },
    )


def cedis_permit_row(row: rx.Var) -> rx.Component:
    selected = State.selected_permit_id == row["id"]
    delete_action = rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            rx.button(
                rx.icon("trash-2", size=14),
                variant="ghost",
                size="1",
                color="#b91c1c",
                _hover={"background": "rgba(185, 28, 28, 0.08)"},
            )
        ),
        rx.alert_dialog.content(
            rx.alert_dialog.title("Eliminar permiso"),
            rx.alert_dialog.description("Esta acción no se puede deshacer."),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button("Cancelar", variant="soft", size="2")
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Eliminar",
                        color_scheme="red",
                        size="2",
                        on_click=State.remove_permit(row["id"]),
                    )
                ),
                justify="end",
                spacing="2",
                width="100%",
            ),
        ),
    )
    return rx.grid(
        rx.hstack(
            rx.button(
                rx.cond(
                    State.permit_files_expanded
                    & (State.selected_permit_id == row["id"]),
                    rx.icon("chevron-up", size=14),
                    rx.icon("chevron-down", size=14),
                ),
                variant="ghost",
                size="1",
                on_click=State.toggle_permit_files_for(row["id"]),
            ),
            rx.text(
                row["nombre"],
                font_size="13px",
                min_width="0",
                overflow="hidden",
                text_overflow="ellipsis",
                white_space="nowrap",
                flex="1",
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        rx.hstack(
            status_badge(row["status"]),
            delete_action,
            spacing="2",
            align="center",
            justify="end",
            width="100%",
        ),
        columns="minmax(0, 1fr) auto",
        spacing="3",
        align="center",
        padding="8px 10px",
        border_radius="10px",
        cursor="pointer",
        background=rx.cond(selected, "rgba(31, 58, 95, 0.12)", "transparent"),
        _hover={"background": "rgba(148, 163, 184, 0.14)"},
        on_click=State.select_permit(row["id"]),
        width="100%",
    )


def permit_file_row(row: rx.Var) -> rx.Component:
    file_url = rx.cond(
        State.use_s3,
        row["url"],
        rx.get_upload_url(row["file"]),
    )
    return rx.grid(
        rx.text(
            row["label"],
            font_size="12px",
            font_weight="500",
            min_width="0",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        rx.hstack(
            rx.link(
                rx.icon("eye", size=18),
                href=file_url,
                is_external=True,
                underline="none",
                color="#1f3a5f",
            ),
            rx.el.a(
                rx.icon("download", size=18),
                href=file_url,
                download=True,
                style={"color": "#1f3a5f"},
            ),
            rx.button(
                rx.icon("trash-2", size=18),
                variant="ghost",
                size="2",
                color="#b91c1c",
                _hover={"background": "rgba(185, 28, 28, 0.08)"},
                on_click=State.remove_permit_pdf(row["id"]),
            ),
            spacing="2",
            align="center",
            justify="start",
        ),
        rx.vstack(
            rx.text_area(
                value=row["comment"],
                on_change=State.set_permit_pdf_comment_local(row["id"]),
                on_blur=State.update_permit_pdf_comment(row["id"], row["comment"]),
                auto_height=True,
                rows="2",
                resize="none",
                min_height="56px",
                background="white",
                border="1px solid #e2e8f0",
                border_radius="8px",
            ),
            spacing="1",
            width="100%",
        ),
        columns="1fr 1fr 1fr",
        spacing="3",
        align="center",
        padding="8px 10px",
        border_bottom="1px solid #e5e7eb",
        background="rgba(248, 250, 252, 0.9)",
        _hover={"background": "rgba(226, 232, 240, 0.6)"},
        width="100%",
    )


def permit_files_section() -> rx.Component:
    return rx.cond(
        State.permit_files_expanded & (State.cedis_initializing == False),
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.text("Archivos", font_size="14px", font_weight="600"),
                    rx.cond(
                        State.permit_files_count != "0",
                        rx.badge(
                            State.permit_files_count,
                            color="#1f3a5f",
                            background="rgba(59, 130, 246, 0.12)",
                            font_size="11px",
                            border_radius="999px",
                        ),
                        rx.box(),
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.cond(
                    State.permit_flow_completed,
                    rx.box(),
                    rx.link(
                        rx.button(
                            rx.hstack(
                                rx.cond(
                                    State.permit_flow_started,
                                    rx.icon("arrow-right", size=14),
                                    rx.icon("file-plus", size=14),
                                ),
                                rx.text(State.permit_flow_label, font_size="12px"),
                                spacing="2",
                                align="center",
                            ),
                            size="2",
                            color_scheme="blue",
                        ),
                        href="/cargar-permiso",
                        underline="none",
                        on_click=State.start_permit_flow,
                    ),
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.box(
                rx.vstack(
                    rx.grid(
                        rx.text("Nombre", font_size="11px", color="#64748b"),
                        rx.text(
                            "Acciones",
                            font_size="11px",
                            color="#64748b",
                            text_align="left",
                            justify_self="start",
                        ),
                        rx.text("Comentarios", font_size="11px", color="#64748b"),
                        columns="1fr 1fr 1fr",
                        spacing="3",
                        align="center",
                        padding="8px 10px",
                        border_bottom="1px solid #e5e7eb",
                        background="rgba(241, 245, 249, 0.9)",
                        width="100%",
                    ),
                    rx.cond(
                        State.permit_files_count != "0",
                        rx.vstack(
                            rx.foreach(State.permit_pdf_items, permit_file_row),
                            spacing="0",
                            width="100%",
                        ),
                        rx.box(
                            rx.text(
                                "Sin archivos",
                                font_size="12px",
                                color="#94a3b8",
                            ),
                            padding="12px",
                            background="rgba(248, 250, 252, 0.9)",
                            width="100%",
                        ),
                    ),
                    spacing="0",
                    width="100%",
                ),
                border="1px solid #e2e8f0",
                border_radius="12px",
                overflow="hidden",
                width="100%",
            ),
            rx.cond(
                State.permit_flow_completed,
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(
                        rx.button(
                            rx.hstack(
                                rx.icon("paperclip", size=14),
                                rx.text("Agregar archivo extra", font_size="12px"),
                                spacing="2",
                                align="center",
                            ),
                            size="2",
                            variant="soft",
                        )
                    ),
                    rx.alert_dialog.content(
                        rx.hstack(
                            rx.alert_dialog.title("Agregar archivo extra"),
                            rx.alert_dialog.cancel(
                                rx.button(rx.icon("x", size=14), variant="ghost", size="1")
                            ),
                            justify="between",
                            align="center",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.vstack(
                                rx.text("Nombre", font_size="12px", color="#64748b"),
                                rx.input(
                                    placeholder="Ej. Anexo tecnico",
                                    value=State.permit_attachment_name,
                                    on_change=State.set_permit_attachment_name,
                                    background="white",
                                    border="1px solid #e2e8f0",
                                    border_radius="10px",
                                    width="100%",
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text("Archivo PDF", font_size="12px", color="#64748b"),
                                rx.upload(
                                    rx.button(
                                        rx.hstack(
                                            rx.icon("upload", size=14),
                                            rx.text("Subir PDF", font_size="12px"),
                                            spacing="2",
                                            align="center",
                                        ),
                                        size="2",
                                        color_scheme="blue",
                                    ),
                                    on_drop=State.handle_permit_attachment_upload,
                                    accept={"application/pdf": [".pdf"]},
                                    multiple=False,
                                ),
                                rx.cond(
                                    State.permit_attachment_uploading,
                                    rx.hstack(
                                        rx.spinner(size="2", color="#2563eb"),
                                        rx.text(
                                            "Subiendo archivo...",
                                            font_size="11px",
                                            color="#2563eb",
                                        ),
                                        spacing="2",
                                        align="center",
                                    ),
                                    rx.box(),
                                ),
                                rx.cond(
                                    State.permit_attachment_file != "",
                                    rx.text(
                                        State.permit_attachment_file,
                                        font_size="11px",
                                        color="#64748b",
                                        overflow_wrap="anywhere",
                                    ),
                                    rx.box(),
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text("Comentarios", font_size="12px", color="#64748b"),
                                rx.text_area(
                                    placeholder="Notas opcionales",
                                    value=State.permit_attachment_comment,
                                    on_change=State.set_permit_attachment_comment,
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
                            rx.cond(
                                State.permit_attachment_error != "",
                                rx.text(
                                    State.permit_attachment_error,
                                    font_size="12px",
                                    color="#b91c1c",
                                ),
                                rx.box(),
                            ),
                            rx.hstack(
                                rx.alert_dialog.cancel(
                                    rx.button("Cancelar", variant="soft", size="2")
                                ),
                                rx.spacer(),
                                rx.button(
                                    "Guardar",
                                    size="2",
                                    color_scheme="blue",
                                    on_click=State.save_permit_attachment,
                                    disabled=rx.cond(
                                        State.permit_attachment_ready, False, True
                                    ),
                                ),
                                width="100%",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                    ),
                    open=State.permit_attachment_open,
                    on_open_change=State.set_permit_attachment_open,
                ),
                rx.box(),
            ),
            spacing="3",
            width="100%",
        ),
        rx.box(),
    )


def cedis_overview_card() -> rx.Component:
    return rx.flex(
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.hstack(
                        rx.text("CEDIS", font_size="16px", font_weight="600"),
                        rx.select(
                            State.cedis_options,
                            value=State.selected_cedis,
                            on_change=State.select_cedis,
                            variant="surface",
                            font_size="14px",
                            font_weight="600",
                            width="auto",
                            min_width="140px",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    rx.alert_dialog.root(
                        rx.alert_dialog.trigger(
                            rx.button(
                                rx.hstack(
                                    rx.icon("pencil", size=14),
                                    rx.text("Editar info", font_size="11px"),
                                    spacing="2",
                                    align="center",
                                ),
                                size="2",
                                variant="solid",
                                on_click=State.open_cedis_edit,
                            )
                        ),
                        rx.alert_dialog.content(
                            rx.hstack(
                                rx.alert_dialog.title("Editar info de CEDIS"),
                                rx.alert_dialog.cancel(
                                    rx.button(
                                        rx.icon("x", size=14),
                                        variant="ghost",
                                        size="1",
                                    )
                                ),
                                justify="between",
                                align="center",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.vstack(
                                    rx.text("Nombre", font_size="12px", color="#64748b"),
                                    rx.input(
                                        value=State.cedis_name,
                                        disabled=True,
                                        background="#f1f5f9",
                                        border="1px solid #e2e8f0",
                                        border_radius="10px",
                                        width="100%",
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                rx.grid(
                                    rx.vstack(
                                        rx.text(
                                            "Dirección",
                                            font_size="12px",
                                            color="#64748b",
                                        ),
                                        rx.input(
                                            placeholder="Dirección del CEDIS",
                                            value=State.cedis_edit_direccion,
                                            on_change=State.set_cedis_edit_direccion,
                                            background="white",
                                            border="1px solid #e2e8f0",
                                            border_radius="10px",
                                            width="100%",
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    rx.vstack(
                                        rx.text(
                                            "Superficie",
                                            font_size="12px",
                                            color="#64748b",
                                        ),
                                        rx.input(
                                            placeholder="25,600 m2",
                                            value=State.cedis_edit_capacity,
                                            on_change=State.set_cedis_edit_capacity,
                                            background="white",
                                            border="1px solid #e2e8f0",
                                            border_radius="10px",
                                            width="100%",
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    rx.vstack(
                                        rx.text(
                                            "No. Empleados",
                                            font_size="12px",
                                            color="#64748b",
                                        ),
                                        rx.input(
                                            placeholder="Cantidad",
                                            value=State.cedis_edit_empleados,
                                            on_change=State.set_cedis_edit_empleados,
                                            background="white",
                                            border="1px solid #e2e8f0",
                                            border_radius="10px",
                                            width="100%",
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    rx.vstack(
                                        rx.text(
                                            "Estatus",
                                            font_size="12px",
                                            color="#64748b",
                                        ),
                                        rx.input(
                                            placeholder="Vigente",
                                            value=State.cedis_edit_status,
                                            on_change=State.set_cedis_edit_status,
                                            background="white",
                                            border="1px solid #e2e8f0",
                                            border_radius="10px",
                                            width="100%",
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    columns={"base": "1fr", "md": "1fr 1fr"},
                                    spacing="3",
                                    width="100%",
                                ),
                                rx.cond(
                                    State.cedis_edit_error != "",
                                    rx.text(
                                        State.cedis_edit_error,
                                        font_size="12px",
                                        color="#dc2626",
                                    ),
                                    rx.box(),
                                ),
                                rx.hstack(
                                    rx.alert_dialog.cancel(
                                        rx.button("Cerrar", variant="soft", size="2")
                                    ),
                                    rx.button(
                                        "Guardar",
                                        color_scheme="green",
                                        size="2",
                                        on_click=State.save_cedis_info,
                                    ),
                                    justify="end",
                                    spacing="2",
                                    width="100%",
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            width="640px",
                        ),
                        open=State.cedis_edit_open,
                        on_open_change=State.set_cedis_edit_open,
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                ),
                rx.box(height="1px", background="#e5e7eb", width="100%"),
                rx.vstack(
                    info_row("Nombre de CEDIS", State.cedis_name),
                    info_row(
                        "Dirección",
                        rx.cond(
                            State.cedis_direccion != "",
                            State.cedis_direccion,
                            "Sin dato",
                        ),
                    ),
                    info_row("Superficie", State.cedis_capacity),
                    info_row(
                        "No. Empleados",
                        rx.cond(
                            State.cedis_empleados != "",
                            State.cedis_empleados,
                            "Sin dato",
                        ),
                    ),
                    rx.vstack(
                        rx.text(
                            "Estatus de permisos",
                            font_size="12px",
                            color="#64748b",
                        ),
                        rx.hstack(
                            rx.foreach(
                                State.cedis_permit_status_mix,
                                lambda entry: rx.box(
                                    height="100%",
                                    width=entry["width"],
                                    background=entry["color"],
                                ),
                            ),
                            spacing="0",
                            height="8px",
                            width="100%",
                            border_radius="999px",
                            overflow="hidden",
                            background="#e2e8f0",
                        ),
                        rx.hstack(
                            rx.foreach(
                                State.cedis_permit_status_mix,
                                lambda entry: rx.hstack(
                                    rx.box(
                                        width="8px",
                                        height="8px",
                                        border_radius="999px",
                                        background=entry["color"],
                                    ),
                                    rx.text(
                                        entry["label"],
                                        font_size="11px",
                                        color="#1e3a8a",
                                        font_weight="600",
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                            ),
                            spacing="3",
                            wrap="wrap",
                            justify="start",
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.box(height="1px", background="#e5e7eb", width="100%"),
                rx.vstack(
                    rx.hstack(
                        rx.text("Permisos", font_size="15px", font_weight="600"),
                        rx.hstack(
                            rx.text(
                                State.cedis_permits,
                                font_size="12px",
                                color="#94a3b8",
                            ),
                            rx.text("permisos", font_size="12px", color="#94a3b8"),
                            spacing="1",
                            align="center",
                        ),
                        justify="between",
                        width="100%",
                    ),
                    rx.cond(
                        State.permit_files_expanded,
                        rx.box(),
                        rx.alert_dialog.root(
                            rx.alert_dialog.trigger(
                                rx.button(
                                    rx.hstack(
                                        rx.icon("plus", size=14),
                                        rx.text("Nuevo Permiso", font_size="12px"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    size="2",
                                    background="rgba(22, 163, 74, 0.14)",
                                    color="#166534",
                                    border="1px solid rgba(22, 163, 74, 0.35)",
                                    width="100%",
                                    _hover={
                                        "background": "#16a34a",
                                        "color": "white",
                                        "border": "1px solid #15803d",
                                    },
                                )
                            ),
                            rx.alert_dialog.content(
                                rx.hstack(
                                    rx.alert_dialog.title("Nuevo permiso"),
                                    rx.alert_dialog.cancel(
                                        rx.button(
                                            rx.icon("x", size=14),
                                            variant="ghost",
                                            size="1",
                                        )
                                    ),
                                    justify="between",
                                    align="center",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.text(
                                                "Nombre",
                                                font_size="12px",
                                                color="#64748b",
                                            ),
                                            rx.text(
                                                "*",
                                                font_size="12px",
                                                color="#dc2626",
                                            ),
                                            spacing="1",
                                            align="center",
                                        ),
                                        rx.input(
                                            placeholder="Nombre del permiso",
                                            value=State.new_permit_name,
                                            on_change=State.set_new_permit_name,
                                            on_key_down=State.add_manual_permit_on_enter,
                                            background="white",
                                            border="1px solid #e2e8f0",
                                            border_radius="10px",
                                            width="100%",
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    rx.cond(
                                        State.new_permit_error != "",
                                        rx.text(
                                            State.new_permit_error,
                                            font_size="12px",
                                            color="#dc2626",
                                        ),
                                        rx.box(),
                                    ),
                                    rx.hstack(
                                        rx.alert_dialog.cancel(
                                            rx.button("Cancelar", variant="soft", size="2")
                                        ),
                                        rx.button(
                                            "Crear",
                                            color_scheme="blue",
                                            size="2",
                                            on_click=State.add_manual_permit,
                                            disabled=State.new_permit_name == "",
                                        ),
                                        justify="end",
                                        spacing="2",
                                        width="100%",
                                    ),
                                    spacing="3",
                                    width="100%",
                                ),
                                width="420px",
                            ),
                            open=State.new_permit_open,
                            on_open_change=State.set_new_permit_open,
                        ),
                    ),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
                rx.vstack(
                    rx.foreach(State.visible_permit_rows, cedis_permit_row),
                    spacing="2",
                    width="100%",
                ),
                permit_files_section(),
                spacing="3",
                width="100%",
            ),
            width="100%",
            padding="20px",
            border_radius="12px",
            border="1px solid #e5e7eb",
            box_shadow="0 14px 30px rgba(15, 23, 42, 0.08)",
            background="white",
        ),
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("Detalles del permiso", font_size="15px", font_weight="600"),
                    rx.cond(
                        State.is_new_permit_selected,
                        rx.box(),
                        status_badge_large(State.permit_status),
                    ),
                    justify="between",
                    width="100%",
                ),
                rx.cond(
                    State.permit_flow_completed
                    & (State.is_new_permit_selected == False),
                    rx.hstack(
                        rx.alert_dialog.root(
                            rx.alert_dialog.trigger(
                                rx.button(
                                    rx.hstack(
                                        rx.icon("refresh-cw", size=14),
                                        rx.text("Actualizar Permiso", font_size="12px"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    size="2",
                                    variant="solid",
                                    color_scheme="blue",
                                )
                            ),
                            rx.alert_dialog.content(
                                rx.hstack(
                                    rx.alert_dialog.title("Actualizar permiso"),
                                    rx.alert_dialog.cancel(
                                        rx.button(
                                            rx.icon("x", size=14),
                                            variant="ghost",
                                            size="1",
                                        )
                                    ),
                                    justify="between",
                                    align="center",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.alert_dialog.description(
                                        "Se movera al historial y se creara uno nuevo."
                                    ),
                                    rx.hstack(
                                        rx.alert_dialog.cancel(
                                            rx.button(
                                                "Cancelar", variant="soft", size="2"
                                            )
                                        ),
                                        rx.alert_dialog.action(
                                            rx.link(
                                                rx.button(
                                                    "Continuar",
                                                    color_scheme="blue",
                                                    size="2",
                                                ),
                                                href="/cargar-permiso",
                                                underline="none",
                                                on_click=State.start_permit_update,
                                            )
                                        ),
                                        justify="end",
                                        spacing="2",
                                        width="100%",
                                    ),
                                    spacing="3",
                                    width="100%",
                                ),
                                width="420px",
                            ),
                        ),
                        justify="start",
                        width="100%",
                    ),
                    rx.box(),
                ),
                permit_detail_rows(),
                rx.vstack(
                    rx.text("Condicionantes", font_size="12px", color="#64748b"),
                    rx.hstack(
                        rx.text(
                            "Responsable",
                            font_size="11px",
                            color="#64748b",
                        ),
                        rx.text(
                            rx.cond(
                                State.is_new_permit_selected,
                                "",
                                rx.cond(
                                    State.permit_responsable != "",
                                    State.permit_responsable,
                                    "Sin responsable",
                                ),
                            ),
                            font_size="12px",
                            font_weight="500",
                            color="#0f172a",
                        ),
                        justify="between",
                        width="100%",
                    ),
                    rx.cond(
                        State.is_new_permit_selected,
                        rx.box(),
                        rx.cond(
                            State.has_permit_condicionantes,
                            rx.box(
                                rx.vstack(
                                    rx.grid(
                                        rx.text(
                                            "Condicionante",
                                            font_size="11px",
                                            color="#64748b",
                                        ),
                                        rx.text(
                                            "Estatus",
                                            font_size="11px",
                                            color="#64748b",
                                            text_align="right",
                                        ),
                                        columns="1fr 170px",
                                        padding="8px 10px",
                                        border_bottom="1px solid #e5e7eb",
                                        background="rgba(241, 245, 249, 0.9)",
                                        width="100%",
                                    ),
                                    rx.foreach(
                                        State.permit_condicionantes_items,
                                        lambda item: rx.grid(
                                            rx.text(
                                                item["text"],
                                                font_size="13px",
                                                font_weight="500",
                                                overflow_wrap="anywhere",
                                            ),
                                            condition_status_select(item),
                                            columns="1fr 170px",
                                            spacing="3",
                                            align="center",
                                            padding="8px 10px",
                                            border_bottom="1px solid #e5e7eb",
                                            background="rgba(248, 250, 252, 0.9)",
                                            width="100%",
                                        ),
                                    ),
                                    spacing="0",
                                    width="100%",
                                ),
                                border="1px solid #e2e8f0",
                                border_radius="12px",
                                overflow="hidden",
                                width="100%",
                            ),
                            rx.text(
                                "Sin condicionantes",
                                font_size="12px",
                                color="#94a3b8",
                            ),
                        ),
                    ),
                    spacing="1",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            width="100%",
            padding="20px",
            border_radius="12px",
            border="1px solid #e5e7eb",
            box_shadow="0 14px 30px rgba(15, 23, 42, 0.08)",
            background="white",
        ),
        direction={"base": "column", "lg": "row"},
        gap="16px",
        align="start",
        width="100%",
    )

def permit_row(row: dict) -> rx.Component:
    return rx.grid(
        rx.text(
            row["nombre"],
            font_size="13px",
            min_width="0",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        rx.text(
            row.get("zona", ""),
            font_size="12px",
            color="#64748b",
            min_width="0",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        rx.text(
            row["cedis"],
            font_size="12px",
            color="#64748b",
            min_width="0",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        rx.text(
            row["vigencia"],
            font_size="12px",
            color="#64748b",
            min_width="0",
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        rx.box(
            status_badge(row["status"]),
            justify_self="end",
        ),
        columns="2fr 1fr 1fr 1fr 1fr",
        spacing="3",
        align="center",
        padding="8px 10px",
        border_radius="10px",
        cursor="pointer",
        _hover={"background": "rgba(148, 163, 184, 0.14)"},
        on_click=State.select_global_permit(row["cedis"], row["id"]),
        width="100%",
    )


def permits_table_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(
                    "Permisos próximos a vencer", font_size="15px", font_weight="600"
                ),
                justify="between",
                width="100%",
            ),
            rx.grid(
                rx.text(
                    "Nombre",
                    font_size="11px",
                    color="#94a3b8",
                    white_space="nowrap",
                ),
                rx.text(
                    "Zona",
                    font_size="11px",
                    color="#94a3b8",
                    white_space="nowrap",
                ),
                rx.text(
                    "CEDIS",
                    font_size="11px",
                    color="#94a3b8",
                    white_space="nowrap",
                ),
                rx.text(
                    "Vigencia",
                    font_size="11px",
                    color="#94a3b8",
                    white_space="nowrap",
                ),
                rx.text(
                    "Estatus",
                    font_size="11px",
                    color="#94a3b8",
                    text_align="right",
                    justify_self="end",
                    white_space="nowrap",
                ),
                columns="2fr 1fr 1fr 1fr 1fr",
                spacing="3",
                align="center",
                padding="0 10px",
                width="100%",
            ),
            rx.vstack(
                rx.foreach(State.expiring_permits, permit_row),
                spacing="2",
                width="100%",
            ),
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


def permit_mix_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Total permisos",
                        font_size="12px",
                        color="#94a3b8",
                    ),
                    rx.hstack(
                        rx.text(
                            State.total_permits,
                            font_size="26px",
                            font_weight="700",
                            color="#0f172a",
                        ),
                        rx.badge(
                            State.vigente_badge,
                            color="#1d4ed8",
                            background="rgba(59, 130, 246, 0.12)",
                            font_size="11px",
                            border_radius="999px",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    rx.text(
                        "Distribución de permisos",
                        font_size="13px",
                        font_weight="600",
                        color="#0f172a",
                    ),
                    rx.text("Por tipo", font_size="11px", color="#94a3b8"),
                    spacing="1",
                    align="start",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("copy", size=14),
                        rx.text("Copiar gráfica", font_size="11px"),
                        spacing="2",
                        align="center",
                    ),
                    on_click=State.copy_permit_mix_chart,
                    variant="soft",
                    size="2",
                ),
                justify="between",
                width="100%",
            ),
            rx.grid(
                rx.box(
                    rx.recharts.pie_chart(
                        rx.recharts.pie(
                            rx.foreach(
                                State.permit_mix,
                                lambda entry: rx.recharts.cell(
                                    fill=entry["color"]
                                ),
                            ),
                            data=State.permit_mix,
                            data_key="value",
                            name_key="name",
                            inner_radius=54,
                            outer_radius=82,
                            padding_angle=3,
                            stroke="#ffffff",
                            stroke_width=2,
                        ),
                        rx.recharts.tooltip(
                    content_style={
                        "backgroundColor": "white",
                        "border": "1px solid #e2e8f0",
                        "borderRadius": "8px",
                        "color": "#0f172a",
                    },
                    cursor={"fill": "rgba(148, 163, 184, 0.15)"},
                ),
                        width="100%",
                        height=200,
                    ),
                    id="permit-mix-chart",
                    width="100%",
                    min_width="180px",
                    max_width="240px",
                    display="flex",
                    justify_content="center",
                ),
                rx.box(
                    rx.vstack(
                        rx.foreach(
                            State.permit_mix,
                            lambda entry: rx.hstack(
                                rx.hstack(
                                    rx.box(
                                        width="10px",
                                        height="10px",
                                        border_radius="999px",
                                        background=entry["color"],
                                    ),
                                    rx.text(
                                        entry["name"],
                                        font_size="12px",
                                        color="#475569",
                                        font_weight="600",
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                                rx.text(
                                    entry["percent_label"],
                                    font_size="12px",
                                    color="#1f2937",
                                    font_weight="600",
                                ),
                                justify="between",
                                width="100%",
                                align="center",
                            ),
                        ),
                        spacing="2",
                        width="100%",
                        max_width="220px",
                    ),
                    display="flex",
                    justify_content="center",
                    width="100%",
                ),
                columns={"base": "1fr", "md": "1fr 1fr"},
                gap="12px",
                width="100%",
                align_items="center",
                justify_items="center",
            ),
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


def _kpi_segment_bar(items: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.foreach(
            items,
            lambda item: rx.box(
                width=item["width"],
                height="8px",
                background=item["color"],
                border_radius="6px",
            ),
        ),
        spacing="1",
        width="100%",
        background="rgba(226, 232, 240, 0.6)",
        padding="2px",
        border_radius="999px",
    )


def _kpi_segment_legend(items: rx.Var) -> rx.Component:
    return rx.flex(
        rx.foreach(
            items,
            lambda item: rx.hstack(
                rx.box(
                    width="8px",
                    height="8px",
                    border_radius="999px",
                    background=item["color"],
                ),
                rx.text(
                    item["name"],
                    font_size="11px",
                    color="#94a3b8",
                ),
                rx.text(
                    item["label"],
                    font_size="12px",
                    font_weight="600",
                    color="#0f172a",
                ),
                spacing="2",
                align="center",
            ),
        ),
        gap="12px",
        wrap="wrap",
        width="100%",
    )


def _dashboard_kpi_card(
    title: str,
    value: rx.Var,
    badge_label: rx.Var,
    badge_color: str,
    badge_bg: str,
    segments: rx.Var,
) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(
                title,
                font_size="13px",
                color="#94a3b8",
            ),
            rx.hstack(
                rx.text(
                    value,
                    font_size="28px",
                    font_weight="700",
                    color="#0f172a",
                ),
                rx.badge(
                    badge_label,
                    color=badge_color,
                    background=badge_bg,
                    font_size="11px",
                    border_radius="999px",
                ),
                spacing="3",
                align="center",
            ),
            _kpi_segment_bar(segments),
            _kpi_segment_legend(segments),
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding="16px",
        border_radius="16px",
        border="1px solid #e5e7eb",
        box_shadow="0 12px 26px rgba(15, 23, 42, 0.08)",
        background="white",
    )


def dashboard_kpi_strip() -> rx.Component:
    return rx.grid(
        _dashboard_kpi_card(
            "Ingresados:",
            State.ingresado_count,
            State.ingresado_badge,
            "#1d4ed8",
            "rgba(59, 130, 246, 0.12)",
            State.ingresado_mix,
        ),
        _dashboard_kpi_card(
            "Vencimientos 90 días",
            State.expiring_risk_total,
            State.expiring_risk_badge,
            "#b45309",
            "rgba(245, 158, 11, 0.16)",
            State.expiring_bucket_mix,
        ),
        columns={"base": "1fr", "lg": "repeat(2, 1fr)"},
        gap="16px",
        width="100%",
    )


def expiration_trend_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.text(
                            "Tendencia de vencimientos",
                            font_size="16px",
                            font_weight="600",
                        ),
                        rx.text(
                            State.expiration_trend_years,
                            font_size="12px",
                            color="#64748b",
                            font_weight="600",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Próximos 12 meses",
                        font_size="11px",
                        color="#94a3b8",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.hstack(
                    rx.badge(
                        State.expiring_soon_count,
                        color="#1d4ed8",
                        background="rgba(59, 130, 246, 0.12)",
                        font_size="11px",
                        border_radius="999px",
                    ),
                    rx.text(
                        "por vencer 90 días",
                        font_size="11px",
                        color="#64748b",
                    ),
                    spacing="2",
                    align="center",
                ),
                justify="between",
                width="100%",
            ),
            rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(
                    stroke_dasharray="4 6", stroke="rgba(148, 163, 184, 0.35)"
                ),
                rx.recharts.bar(
                    data_key="value",
                    fill="#2563eb",
                    radius=[6, 6, 0, 0],
                ),
                rx.recharts.x_axis(data_key="month", tick_line=False),
                rx.recharts.y_axis(
                    allow_decimals=False,
                    tick_count=6,
                    domain=[0, "dataMax"],
                ),
                rx.recharts.tooltip(
                    content_style={
                        "backgroundColor": "white",
                        "border": "1px solid #e2e8f0",
                        "borderRadius": "8px",
                        "color": "#0f172a",
                    },
                    cursor={"fill": "rgba(148, 163, 184, 0.15)"},
                ),
                data=State.expiration_trend,
                width="100%",
                height=260,
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding="18px",
        border_radius="16px",
        border="1px solid #e5e7eb",
        box_shadow="0 14px 30px rgba(15, 23, 42, 0.08)",
        background="white",
    )


def top_risk_cedis_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Riesgo por región",
                        font_size="16px",
                        font_weight="600",
                    ),
                    rx.text(
                        "Mas lejos del centro = mayor % vencido",
                        font_size="11px",
                        color="#94a3b8",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.hstack(
                    rx.badge(
                        State.risk_permits_total,
                        color="#b91c1c",
                        background="rgba(239, 68, 68, 0.12)",
                        font_size="11px",
                        border_radius="999px",
                    ),
                    rx.text(
                        "permisos en riesgo",
                        font_size="11px",
                        color="#64748b",
                    ),
                    spacing="2",
                    align="center",
                ),
                justify="between",
                width="100%",
            ),
            rx.cond(
                State.region_risk_spider,
                rx.recharts.radar_chart(
                    rx.recharts.polar_grid(stroke="#e2e8f0"),
                    rx.recharts.polar_angle_axis(
                        data_key="region",
                        tick_line=False,
                    ),
                    rx.recharts.polar_radius_axis(
                        domain=[0, 100],
                        angle=30,
                        tick_count=6,
                    ),
                    rx.recharts.radar(
                        data_key="vencido_pct",
                        stroke="#f97316",
                        fill="rgba(249, 115, 22, 0.35)",
                        fill_opacity=0.6,
                    ),
                    rx.recharts.tooltip(
                    content_style={
                        "backgroundColor": "white",
                        "border": "1px solid #e2e8f0",
                        "borderRadius": "8px",
                        "color": "#0f172a",
                    },
                    cursor={"fill": "rgba(148, 163, 184, 0.15)"},
                ),
                    data=State.region_risk_spider,
                    width="100%",
                    height=260,
                    outer_radius="70%",
                ),
                rx.box(
                    rx.text(
                        "Sin datos para mostrar.",
                        font_size="12px",
                        color="#94a3b8",
                    ),
                    height="260px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    border="1px dashed #e2e8f0",
                    border_radius="12px",
                ),
            ),
            rx.text(
                "Porcentaje de permisos vencidos por región",
                font_size="11px",
                color="#94a3b8",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding="18px",
        border_radius="16px",
        border="1px solid #e5e7eb",
        box_shadow="0 14px 30px rgba(15, 23, 42, 0.08)",
        background="linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)",
    )


def compliance_histogram_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Progreso de cumplimiento",
                        font_size="16px",
                        font_weight="600",
                    ),
                    rx.text(
                        "Condicionantes completadas por permiso",
                        font_size="11px",
                        color="#94a3b8",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.badge(
                    State.conditions_completion_percent,
                    color="#1d4ed8",
                    background="rgba(59, 130, 246, 0.12)",
                    font_size="11px",
                    border_radius="999px",
                ),
                justify="between",
                width="100%",
            ),
            rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(
                    stroke_dasharray="4 6", stroke="rgba(148, 163, 184, 0.35)"
                ),
                rx.recharts.bar(
                    data_key="value",
                    fill="#3b82f6",
                    radius=[8, 8, 0, 0],
                ),
                rx.recharts.x_axis(data_key="range", tick_line=False),
                rx.recharts.y_axis(allowDecimals=False),
                rx.recharts.tooltip(
                    content_style={
                        "backgroundColor": "white",
                        "border": "1px solid #e2e8f0",
                        "borderRadius": "8px",
                        "color": "#0f172a",
                    },
                    cursor={"fill": "rgba(148, 163, 184, 0.15)"},
                ),
                data=State.compliance_histogram,
                width="100%",
                height=260,
            ),
            rx.hstack(
                rx.text(
                    "Cantidad de permisos:",
                    font_size="11px",
                    color="#94a3b8",
                ),
                rx.text(
                    State.compliance_histogram_total,
                    font_size="11px",
                    font_weight="600",
                    color="#1f3a5f",
                ),
                spacing="1",
                align="center",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding="18px",
        border_radius="16px",
        border="1px solid #e5e7eb",
        box_shadow="0 14px 30px rgba(15, 23, 42, 0.08)",
        background="linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)",
    )


def cedis_status_progress_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.vstack(
                rx.text(
                    "Estatus de permisos",
                    font_size="15px",
                    font_weight="600",
                ),
                rx.text(
                    "Porcentaje del CEDIS seleccionado",
                    font_size="11px",
                    color="#94a3b8",
                ),
                spacing="0",
                align="start",
            ),
            rx.hstack(
                rx.foreach(
                    State.cedis_permit_status_mix,
                    lambda entry: rx.box(
                        height="100%",
                        width=entry["width"],
                        background=entry["color"],
                    ),
                ),
                spacing="0",
                height="10px",
                width="100%",
                border_radius="999px",
                overflow="hidden",
                background="#e2e8f0",
            ),
            rx.hstack(
                rx.foreach(
                    State.cedis_permit_status_mix,
                    lambda entry: rx.hstack(
                        rx.box(
                            width="10px",
                            height="10px",
                            border_radius="999px",
                            background=entry["color"],
                        ),
                        rx.text(
                            entry["label"],
                            font_size="12px",
                            color="#1e3a8a",
                            font_weight="600",
                        ),
                        spacing="2",
                        align="center",
                    ),
                ),
                spacing="4",
                wrap="wrap",
                justify="start",
                width="100%",
            ),
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
