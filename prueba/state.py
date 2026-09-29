"""Gestion de estado del tablero."""

import asyncio
import time
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

import reflex as rx
from sqlalchemy import delete, func, or_, select, update

from .auth import hash_password, verify_password
from .data import (
    DEFAULT_DATA,
    DEFAULT_RANGE,
    DATASETS,
)
from .db import get_session, init_db, seed_db
from .db_models import (
    Cedis,
    Notification,
    Permit as PermitModel,
    PermitCondition,
    PermitPdf,
    PermitStatusHistory,
    User,
    Zone,
)
from .models import Permit as PermitView, PermitSection
from .notifications import send_permit_uploaded
from .pdf_extraction import extract_gov_fields, render_pdf_pages
from .storage import (
    build_file_url,
    build_s3_key,
    delete_pdf_key,
    download_s3_to_temp,
    s3_enabled,
    upload_pdf_bytes,
)
from .state_utils import (
    CONDITION_STATUS_LABELS,
    MONTH_LABELS,
    _build_percent_mix,
    _build_upload_field_boxes,
    _condition_counts,
    _condition_status_counts,
    _label_condition_status,
    _normalize_condition_status,
    _parse_date_string,
    _permit_condition_progress,
    _permit_status_counts,
    _permit_status_counts_with_missing,
    _strip_ingresado,
    status_from_permit,
    status_from_vigencia,
)


class State(rx.State):
    """Estado de la app para interacciones del tablero."""

    active_page: str = "dashboard"
    date_range: str = DEFAULT_RANGE
    search_query: str = ""
    history_query: str = ""
    history_filter_zona: str = "Todos"
    history_filter_cedis: str = "Todos"
    history_filter_responsable: str = "Todos"
    sales_title: str = DEFAULT_DATA["kpis"]["sales"]["title"]
    sales_value: str = DEFAULT_DATA["kpis"]["sales"]["value"]
    sales_delta: str = DEFAULT_DATA["kpis"]["sales"]["delta"]
    sales_trend: str = DEFAULT_DATA["kpis"]["sales"]["trend"]
    visitors_title: str = DEFAULT_DATA["kpis"]["visitors"]["title"]
    visitors_value: str = DEFAULT_DATA["kpis"]["visitors"]["value"]
    visitors_delta: str = DEFAULT_DATA["kpis"]["visitors"]["delta"]
    visitors_trend: str = DEFAULT_DATA["kpis"]["visitors"]["trend"]
    repeat_title: str = DEFAULT_DATA["kpis"]["repeat"]["title"]
    repeat_value: str = DEFAULT_DATA["kpis"]["repeat"]["value"]
    repeat_delta: str = DEFAULT_DATA["kpis"]["repeat"]["delta"]
    repeat_trend: str = DEFAULT_DATA["kpis"]["repeat"]["trend"]
    sales_over_time: list[dict] = DEFAULT_DATA["sales_over_time"]
    visitors_over_time: list[dict] = DEFAULT_DATA["visitors_over_time"]
    customers_over_time: list[dict] = DEFAULT_DATA["customers_over_time"]
    history: list[dict] = DEFAULT_DATA["history"]
    cedis_expanded: bool = True
    db_ready: bool = False
    is_authenticated: bool = False
    current_user_id: int | None = None
    current_user_name: str = ""
    has_users: bool = False
    auth_mode: str = "login"
    auth_username: str = ""
    auth_password: str = ""
    auth_display_name: str = ""
    auth_email: str = ""
    auth_error: str = ""
    auth_info: str = ""
    current_user_email: str = ""
    zona_locations: list[str] = []
    cedis_by_zona: dict[str, list[str]] = {}
    zona_by_cedis: dict[str, str] = {}
    cedis_locations: list[str] = []
    selected_zona: str = ""
    region_choice_made: bool = False
    selected_cedis: str = ""
    selected_permit: str = ""
    selected_permit_id: int | None = None
    cedis_name: str = ""
    cedis_status: str = ""
    cedis_autoridad: str = ""
    cedis_direccion: str = ""
    cedis_empleados: str = ""
    cedis_permiso_medio_ambiente: bool = False
    cedis_permiso_descarga: bool = False
    cedis_equipo_siga: str = ""
    cedis_permits: str = "0"
    cedis_capacity: str = ""
    cedis_edit_open: bool = False
    cedis_edit_status: str = ""
    cedis_edit_direccion: str = ""
    cedis_edit_empleados: str = ""
    cedis_edit_capacity: str = ""
    cedis_edit_error: str = ""
    permit_nombre: str = ""
    permit_asunto: str = ""
    permit_registro: str = ""
    permit_condicionantes: str = ""
    permit_fecha_emision: str = ""
    permit_vigencia: str = ""
    permit_gobierno: str = ""
    permit_numero: str = ""
    permit_scope: str = "Estatal"
    permit_nra: str = ""
    permit_bitacora: str = ""
    permit_cedis: str = ""
    permit_status: str = ""
    permit_responsable: str = ""
    permit_condition_tasks: list[dict] = []
    permit_rows: list[dict] = []
    permit_pdf_items: list[dict] = []
    permit_files_expanded: bool = False
    permit_attachment_open: bool = False
    permit_attachment_name: str = ""
    permit_attachment_comment: str = ""
    permit_attachment_error: str = ""
    permit_attachment_file: str = ""
    permit_attachment_uploading: bool = False
    cedis_initializing: bool = True
    new_permit_open: bool = False
    new_permit_name: str = ""
    new_permit_error: str = ""
    new_permit_id: int | None = None
    permits_by_cedis: dict[str, list[dict]] = {}
    permits_by_cedis_all: dict[str, list[dict]] = {}
    permit_history_rows: list[dict] = []
    upload_nombre: str = ""
    upload_asunto: str = ""
    upload_registro: str = ""
    upload_condicionantes: str = ""
    upload_fecha_emision: str = ""
    upload_vigencia: str = ""
    upload_gobierno: str = ""
    upload_numero: str = ""
    upload_permit_scope: str = ""
    upload_nra: str = ""
    upload_bitacora: str = ""
    upload_cedis: str = ""
    upload_save_error: str = ""
    upload_save_success: str = ""
    upload_save_success_token: str = ""
    notifications: list[dict] = []
    notifications_open: bool = False
    upload_primary_pdf_comment: str = ""
    upload_secondary_pdf_comment: str = ""
    upload_fields_pdf_comment: str = ""
    upload_primary_pdf: str = ""
    upload_secondary_pdf: str = ""
    upload_fields_pdf: str = ""
    upload_use_extraction: bool = True
    upload_extra_pdfs: list[str] = []
    upload_extra_after_step: int = 0
    upload_extra_pdf_label: str = ""
    upload_extra_pdf_comment: str = ""
    upload_step: int = 1
    upload_extract_error: str = ""
    upload_extract_status: str = ""
    upload_extract_loading: bool = False
    upload_is_busy: bool = False
    upload_textract_lines: list[dict] = []
    upload_fields_pages: list[dict] = []
    upload_field_boxes: dict[str, list[dict]] = {}
    upload_highlight_boxes: list[dict] = []
    upload_highlight_field: str = ""
    upload_extract_token: str = ""
    upload_fields_upload_started_at: float | None = None
    replace_mode: bool = False
    replace_target_cedis: str = ""
    replace_target_nombre: str = ""
    replace_target_numero: str = ""

    def set_active_page(self, page: str) -> None:
        self._ensure_db()
        previous = self.active_page
        self.active_page = page
        self.notifications_open = False
        if page != "cargar-permiso":
            self.replace_mode = False
        if previous == "cedis" and page != "cedis":
            self.upload_save_success = ""
            self.upload_save_success_token = ""
            self.permit_files_expanded = False
            self.cedis_initializing = True
        if page == "cedis":
            self.permit_files_expanded = False

    def reset_cedis_view(self) -> None:
        self.permit_files_expanded = False
        self.cedis_initializing = False

    def set_date_range(self, value: str) -> None:
        self.load_date_range(value)

    def set_search_query(self, value: str) -> None:
        self.search_query = value

    def set_history_query(self, value: str) -> None:
        self.history_query = value

    def set_history_filter_zona(self, value: str) -> None:
        self.history_filter_zona = value
        if value == "Todos":
            self.history_filter_cedis = "Todos"
            return
        cedis_list = self.cedis_by_zona.get(value, [])
        if self.history_filter_cedis not in cedis_list:
            self.history_filter_cedis = "Todos"

    def set_history_filter_cedis(self, value: str) -> None:
        self.history_filter_cedis = value

    def set_history_filter_responsable(self, value: str) -> None:
        self.history_filter_responsable = value

    def toggle_notifications(self) -> None:
        self.notifications_open = not self.notifications_open
        if self.notifications_open:
            self._mark_notifications_read()

    def close_notifications(self) -> None:
        self.notifications_open = False

    def clear_notifications(self) -> None:
        if self.current_user_id:
            with get_session() as session:
                session.execute(
                    delete(Notification).where(
                        Notification.user_id == self.current_user_id
                    )
                )
        self.notifications = []
        self.notifications_open = False

    def _push_notification(self, message: str, category: str = "success") -> None:
        if not self.current_user_id:
            return
        with get_session() as session:
            entry = Notification(
                user_id=self.current_user_id,
                message=message,
                category=category,
                read=False,
            )
            session.add(entry)
            session.flush()
            old_ids = (
                session.execute(
                    select(Notification.id)
                    .where(Notification.user_id == self.current_user_id)
                    .order_by(Notification.created_at.desc())
                    .offset(15)
                )
                .scalars()
                .all()
            )
            if old_ids:
                session.execute(delete(Notification).where(Notification.id.in_(old_ids)))
        self._load_notifications()

    def _mark_notifications_read(self) -> None:
        if not self.notifications:
            return
        if self.current_user_id:
            unread_ids = [
                item["id"]
                for item in self.notifications
                if not item.get("read")
            ]
            if unread_ids:
                with get_session() as session:
                    session.execute(
                        update(Notification)
                        .where(Notification.id.in_(unread_ids))
                        .values(read=True)
                    )
        self.notifications = [
            {**item, "read": True} for item in self.notifications
        ]

    def _format_notification_timestamp(self, value: datetime | None) -> str:
        if not value:
            return ""
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        mexico_time = value.astimezone(ZoneInfo("America/Mexico_City"))
        return mexico_time.strftime("%d/%m/%Y %H:%M")

    def _load_notifications(self) -> None:
        if not self.current_user_id:
            self.notifications = []
            return
        with get_session() as session:
            rows = (
                session.execute(
                    select(
                        Notification.id,
                        Notification.message,
                        Notification.category,
                        Notification.created_at,
                        Notification.read,
                    )
                    .where(Notification.user_id == self.current_user_id)
                    .order_by(Notification.created_at.desc())
                    .limit(15)
                )
                .all()
            )
        self.notifications = [
            {
                "id": row.id,
                "message": row.message,
                "timestamp": self._format_notification_timestamp(row.created_at),
                "category": row.category,
                "read": row.read,
            }
            for row in rows
        ]

    def _permit_saved_message(self, name: str | None) -> str:
        cleaned = (name or "").strip()
        if cleaned:
            return f"{cleaned} guardado correctamente."
        return "Permiso guardado correctamente."

    def set_auth_username(self, value: str) -> None:
        self.auth_username = value

    def set_auth_password(self, value: str) -> None:
        self.auth_password = value

    def set_auth_display_name(self, value: str) -> None:
        self.auth_display_name = value

    def set_auth_email(self, value: str) -> None:
        self.auth_email = value

    def _ensure_db(self) -> None:
        if self.db_ready:
            #init_db()
            return
        init_db()
        seed_db()
        permit_id = None
        with get_session() as session:
            self.has_users = bool(session.execute(select(User.id)).first())
        self.auth_mode = "login" if self.has_users else "register"
        self.db_ready = True
        self._load_reference_data()
        self._load_permits_cache()
        self._apply_default_selection()
        self._refresh_selected_cedis()

    def load_auth_state(self) -> None:
        self._ensure_db()
        with get_session() as session:
            self.has_users = bool(session.execute(select(User.id)).first())
        self.auth_mode = "login" if self.has_users else "register"

    def set_auth_mode_login(self) -> None:
        self.auth_mode = "login"
        self.auth_error = ""
        self.auth_info = ""

    def set_auth_mode_register(self) -> None:
        self.auth_mode = "register"
        self.auth_error = ""
        self.auth_info = ""

    def request_password_reset(self) -> None:
        self.auth_error = ""
        self.auth_info = "Contacta al administrador para restablecer tu contraseña."

    def create_first_user(self) -> None:
        self.register_user()

    def register_user(self) -> None:
        self._ensure_db()
        self.auth_error = ""
        self.auth_info = ""
        username = self.auth_username.strip()
        password = self.auth_password
        display_name = self.auth_display_name.strip() or username
        email = self.auth_email.strip()
        if not username or not password or not email:
            self.auth_error = "Usuario, correo y contraseña requeridos."
            return
        if "@" not in email or "." not in email:
            self.auth_error = "Correo invalido."
            return
        with get_session() as session:
            exists = session.execute(
                select(User.id).where(User.username == username)
            ).first()
            if exists:
                self.auth_error = "El usuario ya existe."
                return
            email_exists = session.execute(
                select(User.id).where(User.email == email)
            ).first()
            if email_exists:
                self.auth_error = "El correo ya esta registrado."
                return
            user = User(
                username=username,
                display_name=display_name,
                email=email,
                password_hash=hash_password(password),
            )
            session.add(user)
            session.flush()
            user_id = user.id
        self.current_user_id = user_id
        self.current_user_name = display_name
        self.current_user_email = email
        self.is_authenticated = True
        self.has_users = True
        self._load_permits_cache()
        self._refresh_selected_cedis()
        self._load_notifications()
        self.auth_mode = "login"
        self.auth_password = ""
        self.auth_display_name = ""
        self.auth_email = ""
        self.auth_error = ""
        self.auth_info = ""

    def submit_auth(self) -> None:
        if self.auth_mode == "register" or not self.has_users:
            self.register_user()
        else:
            self.login()

    def login(self) -> None:
        self._ensure_db()
        self.auth_error = ""
        self.auth_info = ""
        username = self.auth_username.strip()
        password = self.auth_password
        if not username or not password:
            self.auth_error = "Usuario y contraseña requeridos."
            return
        with get_session() as session:
            row = session.execute(
                select(
                    User.id,
                    User.username,
                    User.display_name,
                    User.email,
                    User.password_hash,
                ).where(User.username == username)
            ).first()
        if not row:
            self.auth_error = "Credenciales incorrectas."
            return
        user_id, user_name, display_name, user_email, password_hash = row
        if not verify_password(password, password_hash):
            self.auth_error = "Credenciales incorrectas."
            return
        self.current_user_id = user_id
        self.current_user_name = display_name or user_name
        self.current_user_email = user_email or ""
        self.is_authenticated = True
        self._load_permits_cache()
        self._refresh_selected_cedis()
        self._load_notifications()
        self.auth_mode = "login"
        self.auth_password = ""
        self.auth_error = ""
        self.auth_info = ""

    def logout(self) -> None:
        self.current_user_id = None
        self.current_user_email = ""
        self.current_user_name = ""
        self.is_authenticated = False
        self.notifications = []
        self.notifications_open = False
        self.auth_password = ""
        self.auth_error = ""
        self.auth_info = ""
        self.auth_mode = "login" if self.has_users else "register"

    def _load_reference_data(self) -> None:
        with get_session() as session:
            zona_locations = (
                session.execute(select(Zone.name).order_by(Zone.sort_order))
                .scalars()
                .all()
            )
            cedis_rows = (
                session.execute(
                    select(Cedis.name, Zone.name)
                    .join(Zone, Cedis.zone_id == Zone.id)
                    .order_by(Zone.sort_order, Cedis.sort_order)
                )
                .all()
            )
        cedis_by_zona: dict[str, list[str]] = {zona: [] for zona in zona_locations}
        zona_by_cedis: dict[str, str] = {}
        cedis_locations: list[str] = []
        for cedis_name, zona_name in cedis_rows:
            cedis_locations.append(cedis_name)
            cedis_by_zona.setdefault(zona_name, []).append(cedis_name)
            zona_by_cedis[cedis_name] = zona_name
        self.zona_locations = zona_locations
        self.cedis_by_zona = cedis_by_zona
        self.zona_by_cedis = zona_by_cedis
        self.cedis_locations = cedis_locations

    def _apply_default_selection(self) -> None:
        if not self.zona_locations:
            return
        if self.selected_zona not in self.zona_locations:
            self.selected_zona = self.zona_locations[0]
        cedis_list = self.cedis_by_zona.get(self.selected_zona, [])
        if not cedis_list and self.cedis_locations:
            cedis_list = [self.cedis_locations[0]]
        if self.selected_cedis not in self.cedis_locations:
            self.selected_cedis = cedis_list[0] if cedis_list else ""
        if not self.upload_cedis and self.selected_cedis:
            self.upload_cedis = self.selected_cedis

    def _parse_input_date(self, value: str) -> date | None:
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return None

    def _parse_vigencia_date(self, value: str | date | None) -> date | None:
        if isinstance(value, date):
            return value
        if not value or value == "-":
            return None
        return _parse_date_string(value)

    def _format_date_display(self, value: str | date | None) -> str:
        if not value or value == "-":
            return "-"
        if isinstance(value, date):
            return value.strftime("%d/%m/%Y")
        parsed = _parse_date_string(value)
        if parsed:
            return parsed.strftime("%d/%m/%Y")
        return value

    def _serialize_permit(
        self,
        permit: PermitModel,
        cedis_name: str,
        pdfs: list[PermitPdf],
        conditions: list[dict],
        responsable: str | None = None,
    ) -> dict:
        fecha_emision = self._format_date_display(permit.fecha_emision)
        vigencia = self._format_date_display(permit.vigencia)
        pdf_items: list[dict] = []
        for index, pdf in enumerate(pdfs):
            label = pdf.label or f"PDF {index + 1}"
            display_label = "Pago de derechos" if label.lower() == "derechos" else label
            pdf_items.append(
                {
                    "id": pdf.id,
                    "file": pdf.s3_key,
                    "label": display_label,
                    "kind": pdf.kind or "",
                    "comment": pdf.comment or "",
                    "order_index": pdf.order_index,
                    "url": self._pdf_url(pdf.s3_key),
                }
            )
        permit_data = {
            "id": permit.id,
            "nombre": permit.nombre,
            "asunto": permit.asunto or permit.nombre,
            "registro": permit.registro or "",
            "gobierno": permit.gobierno or "",
            "numero": permit.numero or "",
            "permit_scope": permit.permit_scope or "Estatal",
            "nra": permit.nra or "",
            "bitacora": permit.bitacora or "",
            "fecha_emision": fecha_emision,
            "vigencia": vigencia,
            "cedis": cedis_name,
            "pdfs": [pdf.s3_key for pdf in pdfs],
            "pdf_items": pdf_items,
            "condicionantes": list(conditions),
            "responsable": responsable or "",
        }
        permit_data["status"] = status_from_permit(permit_data)
        return permit_data

    def _load_permits_cache(self) -> None:
        with get_session() as session:
            self._backfill_created_by_if_single_user(session)
            self.permits_by_cedis = self._fetch_permits_by_cedis(
                session, filter_user=True, include_archived=False
            )
            self.permits_by_cedis_all = self._fetch_permits_by_cedis(
                session, filter_user=False, include_archived=True
            )
            self.permit_history_rows = self._fetch_permit_history(
                session, filter_user=False
            )

    def _fetch_permits_by_cedis(
        self,
        session,
        *,
        filter_user: bool = True,
        include_archived: bool = False,
    ) -> dict[str, list[dict]]:
        query = (
            select(PermitModel, Cedis.name, User.display_name, User.username)
            .join(Cedis, PermitModel.cedis_id == Cedis.id)
            .outerjoin(User, PermitModel.created_by_id == User.id)
        )
        if not include_archived:
            query = query.where(
                or_(
                    PermitModel.archived.is_(False),
                    PermitModel.archived.is_(None),
                )
            )
        permits = (
            session.execute(
                query.order_by(
                    Cedis.sort_order, PermitModel.sort_order, PermitModel.nombre
                )
            )
            .all()
        )
        if not permits:
            return {}
        current_user_id = self.current_user_id if filter_user else None
        current_user_name = (self.current_user_name or "").strip() if filter_user else ""
        permit_ids = [permit.id for permit, *_ in permits]
        pdfs_by_permit: dict[int, list[PermitPdf]] = defaultdict(list)
        conditions_by_permit: dict[int, list[dict]] = defaultdict(list)
        if permit_ids:
            pdf_rows = (
                session.execute(
                    select(PermitPdf)
                    .where(PermitPdf.permit_id.in_(permit_ids))
                    .order_by(PermitPdf.order_index)
                )
                .scalars()
                .all()
            )
            for pdf in pdf_rows:
                pdfs_by_permit[pdf.permit_id].append(pdf)
            condition_rows = (
                session.execute(
                    select(PermitCondition)
                    .where(PermitCondition.permit_id.in_(permit_ids))
                    .order_by(PermitCondition.position)
                )
                .scalars()
                .all()
            )
            for condition in condition_rows:
                conditions_by_permit[condition.permit_id].append(
                    {
                        "id": condition.id,
                        "text": condition.text,
                        "status": _label_condition_status(condition.status),
                        "position": condition.position,
                    }
                )
        grouped: dict[str, list[dict]] = defaultdict(list)
        for permit, cedis_name, display_name, username in permits:
            responsable = display_name or username or ""
            if current_user_id and filter_user:
                if permit.created_by_id != current_user_id and (
                    not current_user_name or responsable != current_user_name
                ):
                    continue
            grouped[cedis_name].append(
                self._serialize_permit(
                    permit,
                    cedis_name,
                    pdfs_by_permit.get(permit.id, []),
                    conditions_by_permit.get(permit.id, []),
                    responsable,
                )
            )
        return dict(grouped)

    def _fetch_permit_history(
        self, session, *, filter_user: bool = True
    ) -> list[dict]:
        permits = (
            session.execute(
                select(
                    PermitModel,
                    Cedis.name,
                    Zone.name,
                    User.display_name,
                    User.username,
                )
                .join(Cedis, PermitModel.cedis_id == Cedis.id)
                .join(Zone, Cedis.zone_id == Zone.id)
                .outerjoin(User, PermitModel.created_by_id == User.id)
                .where(PermitModel.archived.is_(True))
                .order_by(PermitModel.updated_at.desc(), PermitModel.id.desc())
            )
            .all()
        )
        if not permits:
            return []
        current_user_id = self.current_user_id if filter_user else None
        current_user_name = (self.current_user_name or "").strip() if filter_user else ""
        permit_ids = [permit.id for permit, *_ in permits]
        pdfs_by_permit: dict[int, list[PermitPdf]] = defaultdict(list)
        conditions_by_permit: dict[int, list[dict]] = defaultdict(list)
        if permit_ids:
            pdf_rows = (
                session.execute(
                    select(PermitPdf)
                    .where(PermitPdf.permit_id.in_(permit_ids))
                    .order_by(PermitPdf.order_index)
                )
                .scalars()
                .all()
            )
            for pdf in pdf_rows:
                pdfs_by_permit[pdf.permit_id].append(pdf)
            condition_rows = (
                session.execute(
                    select(PermitCondition)
                    .where(PermitCondition.permit_id.in_(permit_ids))
                    .order_by(PermitCondition.position)
                )
                .scalars()
                .all()
            )
            for condition in condition_rows:
                conditions_by_permit[condition.permit_id].append(
                    {
                        "id": condition.id,
                        "text": condition.text,
                        "status": _label_condition_status(condition.status),
                        "position": condition.position,
                    }
                )
        rows: list[dict] = []
        for permit, cedis_name, zona_name, display_name, username in permits:
            responsable = display_name or username or ""
            if not responsable and permit.created_by_id:
                responsable = f"Usuario {permit.created_by_id}"
            if current_user_id and filter_user:
                if permit.created_by_id != current_user_id and (
                    not current_user_name or responsable != current_user_name
                ):
                    continue
            permit_data = self._serialize_permit(
                permit,
                cedis_name,
                pdfs_by_permit.get(permit.id, []),
                conditions_by_permit.get(permit.id, []),
                responsable,
            )
            permit_data["zona"] = zona_name
            permit_data["pdfs_count"] = str(len(permit_data.get("pdf_items", [])))
            rows.append(permit_data)
        return rows

    def _backfill_created_by_if_single_user(self, session) -> None:
        user_ids = (
            session.execute(select(User.id).order_by(User.id))
            .scalars()
            .all()
        )
        if len(user_ids) != 1:
            return
        user_id = user_ids[0]
        session.execute(
            update(PermitModel)
            .where(PermitModel.created_by_id.is_(None))
            .values(created_by_id=user_id)
        )

    def _clear_selected_permit(self) -> None:
        self.selected_permit = ""
        self.selected_permit_id = None
        self.permit_nombre = ""
        self.permit_asunto = ""
        self.permit_registro = ""
        self.permit_condicionantes = ""
        self.permit_fecha_emision = ""
        self.permit_vigencia = ""
        self.permit_gobierno = ""
        self.permit_numero = ""
        self.permit_scope = "Estatal"
        self.permit_nra = ""
        self.permit_bitacora = ""
        self.permit_cedis = ""
        self.permit_status = ""
        self.permit_responsable = ""
        self.permit_condition_tasks = []
        self.permit_pdf_items = []

    def _refresh_selected_cedis(self) -> None:
        if not self.selected_cedis:
            self._clear_selected_permit()
            return
        with get_session() as session:
            row = (
                session.execute(
                    select(
                        Cedis.name,
                        Cedis.status,
                        Cedis.autoridad,
                        Cedis.direccion,
                        Cedis.empleados,
                        Cedis.permiso_medio_ambiente_municipal,
                        Cedis.permiso_descarga_municipal,
                        Cedis.equipo_siga,
                        Cedis.capacity,
                    ).where(Cedis.name == self.selected_cedis)
                )
                .first()
            )
        if not row:
            self._clear_selected_permit()
            return
        (
            cedis_name,
            status,
            autoridad,
            direccion,
            empleados,
            permiso_medio_ambiente,
            permiso_descarga,
            equipo_siga,
            capacity,
        ) = row
        self.selected_zona = self.zona_by_cedis.get(cedis_name, self.selected_zona)
        self.cedis_name = cedis_name
        self.cedis_status = status or ""
        self.cedis_autoridad = autoridad or ""
        self.cedis_direccion = direccion or ""
        self.cedis_empleados = empleados or ""
        self.cedis_permiso_medio_ambiente = bool(permiso_medio_ambiente)
        self.cedis_permiso_descarga = bool(permiso_descarga)
        self.cedis_equipo_siga = equipo_siga or ""
        self.cedis_capacity = capacity or ""
        self.permit_rows = self.permits_by_cedis_all.get(cedis_name, [])
        self.cedis_permits = str(len(self.permit_rows))
        if self.permit_rows:
            self.select_permit(self.permit_rows[0]["id"])
        else:
            self._clear_selected_permit()

    def _refresh_selected_permit(self) -> None:
        if not self.selected_cedis:
            self._clear_selected_permit()
            return
        self.permit_rows = self.permits_by_cedis_all.get(self.selected_cedis, [])
        self.cedis_permits = str(len(self.permit_rows))
        if not self.permit_rows:
            self._clear_selected_permit()
            return
        target_id = self.selected_permit_id
        if target_id is None:
            target_id = self.permit_rows[0].get("id")
        if target_id is None or not any(
            row.get("id") == target_id for row in self.permit_rows
        ):
            target_id = self.permit_rows[0].get("id")
        if target_id is None:
            self._clear_selected_permit()
            return
        self.select_permit(target_id)

    def _delete_permit_db(self, session, permit_id: int) -> bool:
        permit = session.get(PermitModel, permit_id)
        if not permit:
            return False
        session.delete(permit)
        return True

    def copy_permit_mix_chart(self) -> rx.event.EventSpec:
        script = """
        (async () => {
          const container = document.getElementById("permit-mix-chart");
          if (!container) {
            console.warn("permit-mix-chart not found");
            return;
          }
          const svg = container.querySelector("svg");
          if (!svg) {
            console.warn("chart svg not found");
            return;
          }
          const rect = svg.getBoundingClientRect();
          const width = Math.max(1, Math.ceil(rect.width));
          const height = Math.max(1, Math.ceil(rect.height));
          const serializer = new XMLSerializer();
          const svgData = serializer.serializeToString(svg);
          const blob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
          const url = URL.createObjectURL(blob);
          const img = new Image();
          const canvas = document.createElement("canvas");
          const scale = window.devicePixelRatio || 1;
          canvas.width = width * scale;
          canvas.height = height * scale;
          const ctx = canvas.getContext("2d");
          ctx.scale(scale, scale);
          ctx.fillStyle = "#ffffff";
          ctx.fillRect(0, 0, width, height);
          img.onload = async () => {
            ctx.drawImage(img, 0, 0, width, height);
            URL.revokeObjectURL(url);
            const dataUrl = canvas.toDataURL("image/png");
            if (navigator.clipboard && window.ClipboardItem) {
              canvas.toBlob(async (blobPng) => {
                try {
                  await navigator.clipboard.write([
                    new ClipboardItem({ "image/png": blobPng }),
                  ]);
                } catch (err) {
                  const link = document.createElement("a");
                  link.href = dataUrl;
                  link.download = "grafica-permisos.png";
                  link.click();
                }
              }, "image/png");
            } else {
              const link = document.createElement("a");
              link.href = dataUrl;
              link.download = "grafica-permisos.png";
              link.click();
            }
          };
          img.onerror = () => {
            URL.revokeObjectURL(url);
          };
          img.src = url;
        })();
        """
        return rx.event.call_script(script)

    def select_search_result(self, cedis: str, permit_id: int) -> None:
        self.search_query = ""
        self.select_global_permit(cedis, permit_id)

    def set_upload_nombre(self, value: str) -> None:
        self.upload_nombre = value
        self.upload_asunto = value

    def set_upload_asunto(self, value: str) -> None:
        self.upload_asunto = value
        self.upload_nombre = value

    def set_upload_registro(self, value: str) -> None:
        self.upload_registro = value

    def set_upload_condicionantes(self, value: str) -> None:
        self.upload_condicionantes = value

    def set_upload_condicionante_item(self, index: int, value: str) -> None:
        lines = self.upload_condicionantes.split("\n")
        if index < 0:
            return
        if index >= len(lines):
            lines.extend([""] * (index + 1 - len(lines)))
        lines[index] = value
        self.upload_condicionantes = "\n".join(lines)

    def add_upload_condicionante(self) -> None:
        lines = self.upload_condicionantes.split("\n")
        lines.append("")
        self.upload_condicionantes = "\n".join(lines)

    def remove_upload_condicionante(self, index: int) -> None:
        lines = self.upload_condicionantes.split("\n")
        if not lines:
            return
        if index < 0 or index >= len(lines):
            return
        lines.pop(index)
        if not lines:
            lines = [""]
        self.upload_condicionantes = "\n".join(lines)

    def set_upload_fecha_emision(self, value: str) -> None:
        self.upload_fecha_emision = value

    def set_upload_vigencia(self, value: str) -> None:
        self.upload_vigencia = value

    def set_upload_gobierno(self, value: str) -> None:
        self.upload_gobierno = value

    def set_upload_numero(self, value: str) -> None:
        self.upload_numero = value

    def set_upload_nra(self, value: str) -> None:
        self.upload_nra = value

    def set_upload_bitacora(self, value: str) -> None:
        self.upload_bitacora = value

    def set_upload_permit_scope(self, value: str):
        cleaned = value if value in {"Municipal", "Estatal", "Federal", ""} else ""
        if cleaned == self.upload_permit_scope:
            return
        self.upload_permit_scope = cleaned
        self.upload_extract_error = ""
        self.upload_extract_status = ""
        self.upload_highlight_boxes = []
        self.upload_highlight_field = ""
        if not self.upload_fields_pdf or not self.upload_use_extraction:
            return
        self.upload_extract_token = uuid4().hex
        self.upload_extract_loading = True
        yield
        return type(self).extract_fields_background(
            self.upload_fields_pdf, self.upload_extract_token
        )

    def set_upload_primary_pdf_comment(self, value: str) -> None:
        self.upload_primary_pdf_comment = value

    def set_upload_secondary_pdf_comment(self, value: str) -> None:
        self.upload_secondary_pdf_comment = value

    def set_upload_fields_pdf_comment(self, value: str) -> None:
        self.upload_fields_pdf_comment = value

    def set_upload_extra_pdf_label(self, value: str) -> None:
        self.upload_extra_pdf_label = value

    def set_upload_extra_pdf_comment(self, value: str) -> None:
        self.upload_extra_pdf_comment = value

    def set_upload_cedis(self, value: str) -> None:
        self.upload_cedis = value

    def open_cedis_edit(self) -> None:
        if not self.selected_cedis:
            self.cedis_edit_error = "Selecciona un CEDIS."
            return
        self.cedis_edit_status = self.cedis_status
        self.cedis_edit_direccion = self.cedis_direccion
        self.cedis_edit_empleados = self.cedis_empleados
        self.cedis_edit_capacity = self.cedis_capacity
        self.cedis_edit_error = ""
        self.cedis_edit_open = True

    def set_cedis_edit_open(self, value: bool) -> None:
        self.cedis_edit_open = value
        if not value:
            self.cedis_edit_error = ""

    def set_cedis_edit_status(self, value: str) -> None:
        self.cedis_edit_status = value
        self.cedis_edit_error = ""

    def set_cedis_edit_direccion(self, value: str) -> None:
        self.cedis_edit_direccion = value
        self.cedis_edit_error = ""

    def set_cedis_edit_empleados(self, value: str) -> None:
        self.cedis_edit_empleados = value
        self.cedis_edit_error = ""

    def set_cedis_edit_capacity(self, value: str) -> None:
        self.cedis_edit_capacity = value
        self.cedis_edit_error = ""

    def save_cedis_info(self) -> None:
        self._ensure_db()
        if not self.selected_cedis:
            self.cedis_edit_error = "Selecciona un CEDIS."
            return
        with get_session() as session:
            cedis = (
                session.execute(
                    select(Cedis).where(Cedis.name == self.selected_cedis)
                )
                .scalars()
                .first()
            )
            if not cedis:
                self.cedis_edit_error = "CEDIS no encontrado."
                return
            cedis.status = self.cedis_edit_status.strip()
            cedis.direccion = self.cedis_edit_direccion.strip()
            cedis.empleados = self.cedis_edit_empleados.strip()
            cedis.capacity = self.cedis_edit_capacity.strip()
        self.cedis_status = self.cedis_edit_status.strip()
        self.cedis_direccion = self.cedis_edit_direccion.strip()
        self.cedis_empleados = self.cedis_edit_empleados.strip()
        self.cedis_capacity = self.cedis_edit_capacity.strip()
        self.cedis_edit_open = False
        self.cedis_edit_error = ""

    def set_permit_attachment_name(self, value: str) -> None:
        self.permit_attachment_name = value
        self.permit_attachment_error = ""

    def set_permit_attachment_comment(self, value: str) -> None:
        self.permit_attachment_comment = value
        self.permit_attachment_error = ""

    def set_permit_attachment_open(self, value: bool) -> None:
        self.reset_permit_attachment_form()
        self.permit_attachment_open = value

    def set_new_permit_name(self, value: str) -> None:
        self.new_permit_name = value
        self.new_permit_error = ""

    def add_manual_permit_on_enter(self, key: str) -> None:
        if key != "Enter":
            return
        self.add_manual_permit()

    def reset_new_permit_form(self) -> None:
        self.new_permit_name = ""
        self.new_permit_error = ""

    def set_new_permit_open(self, value: bool) -> None:
        self.reset_new_permit_form()
        self.new_permit_open = value

    def _cleanup_upload_preview_files(self) -> None:
        if not self.upload_fields_pages:
            return
        upload_dir = rx.get_upload_dir()
        for page in self.upload_fields_pages:
            if not isinstance(page, dict):
                continue
            filename = str(page.get("file", "")).strip()
            if not filename:
                continue
            if Path(filename).suffix.lower() != ".png":
                continue
            path = upload_dir / Path(filename).name
            try:
                path.unlink()
            except FileNotFoundError:
                continue
            except OSError:
                continue

    def _reset_upload_preview_state(self) -> None:
        self.upload_extract_token = uuid4().hex
        self.upload_textract_lines = []
        self.upload_fields_pages = []
        self.upload_field_boxes = {}
        self.upload_highlight_boxes = []
        self.upload_highlight_field = ""

    def select_upload_field(self, field_key: str) -> None:
        if self.upload_highlight_field == field_key:
            self.upload_highlight_field = ""
            self.upload_highlight_boxes = []
            return
        self.upload_highlight_field = field_key
        boxes = self.upload_field_boxes.get(field_key, [])
        self.upload_highlight_boxes = boxes
        if not boxes:
            return
        first_page = min(int(box.get("page", 1)) for box in boxes)
        script = (
            "(() => {"
            f"const el = document.getElementById('upload-page-{first_page}');"
            "if (el) { el.scrollIntoView({behavior: 'smooth', block: 'start'}); }"
            "})();"
        )
        return rx.event.call_script(script)

    def _pdf_name(self, key: str) -> str:
        return Path(key).name if key else ""

    def _pdf_url(self, key: str) -> str:
        if not key:
            return ""
        if s3_enabled():
            return build_file_url(key)
        return ""

    def _resolve_pdf_for_extraction(self, stored_name: str) -> tuple[Path, bool]:
        if not s3_enabled():
            return rx.get_upload_dir() / stored_name, False
        local_path = rx.get_upload_dir() / Path(stored_name).name
        if local_path.exists():
            return local_path, True
        return download_s3_to_temp(stored_name), True

    def _save_uploads(
        self, files: list[rx.UploadFile], keep_local: bool = False
    ) -> list[str]:
        upload_dir = rx.get_upload_dir()
        saved_files: list[str] = []
        for file in files:
            if not file.name:
                continue
            name = Path(file.name).name
            stored_name = f"{uuid4().hex}_{name}"
            data = file.file.read()
            if not data:
                continue
            if s3_enabled():
                key = build_s3_key(stored_name)
                upload_pdf_bytes(data, key)
                if keep_local:
                    local_path = upload_dir / Path(key).name
                    local_path.write_bytes(data)
                saved_files.append(key)
            else:
                destination = upload_dir / stored_name
                destination.write_bytes(data)
                saved_files.append(stored_name)
        return saved_files

    def handle_primary_upload(self, files: list[rx.UploadFile]) -> None:
        self.upload_is_busy = True
        self.upload_save_success = ""
        self.upload_save_success_token = ""
        yield
        saved_files = self._save_uploads(files)
        self.upload_is_busy = False
        if not saved_files:
            return
        self.upload_primary_pdf = saved_files[0]

    def handle_secondary_upload(self, files: list[rx.UploadFile]) -> None:
        self.upload_is_busy = True
        self.upload_save_success = ""
        self.upload_save_success_token = ""
        yield
        saved_files = self._save_uploads(files)
        self.upload_is_busy = False
        if not saved_files:
            return
        self.upload_secondary_pdf = saved_files[0]

    def handle_fields_upload(self, files: list[rx.UploadFile]) -> None:
        self._cleanup_upload_preview_files()
        if not self.upload_permit_scope:
            self.upload_extract_error = "Selecciona la autoridad antes de subir el PDF."
            return
        self.upload_is_busy = True
        self.upload_save_success = ""
        self.upload_save_success_token = ""
        yield
        self.upload_fields_upload_started_at = time.perf_counter()
        upload_start = self.upload_fields_upload_started_at
        saved_files = self._save_uploads(files, keep_local=True)
        upload_elapsed = time.perf_counter() - upload_start
        print(f"[timing] permit PDF upload saved in {upload_elapsed:.2f}s")
        self.upload_is_busy = False
        if not saved_files:
            self.upload_fields_upload_started_at = None
            return
        self.upload_fields_pdf = saved_files[-1]
        self.upload_extract_token = uuid4().hex
        self.upload_extract_error = ""
        self.upload_extract_status = ""
        self.upload_textract_lines = []
        self.upload_fields_pages = []
        self.upload_field_boxes = {}
        self.upload_highlight_boxes = []
        self.upload_highlight_field = ""
        if not self.upload_use_extraction:
            self.upload_extract_loading = False
            return
        self.upload_extract_loading = True
        yield
        return type(self).extract_fields_background(saved_files[-1], self.upload_extract_token)

    @rx.event(background=True)
    async def extract_fields_background(self, stored_name: str, extract_token: str) -> None:
        cleanup_path: Path | None = None
        try:
            pdf_path, should_cleanup = self._resolve_pdf_for_extraction(stored_name)
            if should_cleanup:
                cleanup_path = pdf_path
            fields, lines = await asyncio.to_thread(
                extract_gov_fields, pdf_path, scope=self.upload_permit_scope
            )
            prefix = f"{Path(stored_name).stem}_{uuid4().hex}"
            pages = await asyncio.to_thread(
                render_pdf_pages, pdf_path, rx.get_upload_dir(), prefix
            )
            field_boxes = _build_upload_field_boxes(
                fields, lines, self.upload_permit_scope
            )
        except Exception as exc:
            async with self:
                if self.upload_extract_token != extract_token:
                    return
                if not self.upload_use_extraction:
                    self.upload_extract_error = ""
                    self.upload_extract_status = ""
                    self.upload_extract_loading = False
                    return
                self.upload_extract_error = f"Error al extraer campos: {exc}"
                self.upload_extract_loading = False
                self.upload_textract_lines = []
                self.upload_fields_pages = []
                self.upload_field_boxes = {}
                self.upload_highlight_boxes = []
                self.upload_highlight_field = ""
            return
        else:
            async with self:
                if self.upload_extract_token != extract_token:
                    return
                if not self.upload_use_extraction:
                    self.upload_extract_error = ""
                    self.upload_extract_status = ""
                    self.upload_extract_loading = False
                    return
                scope_key = (self.upload_permit_scope or "Estatal").strip().lower()
                if scope_key in {"federal", "federacion"}:
                    if fields.nombre:
                        self.upload_nombre = fields.nombre
                        self.upload_asunto = fields.nombre
                    elif fields.nombre is not None:
                        self.upload_nombre = ""
                        self.upload_asunto = ""
                    if getattr(fields, "nra", None):
                        self.upload_nra = fields.nra
                    elif getattr(fields, "nra", None) is not None:
                        self.upload_nra = ""
                    if getattr(fields, "bitacora", None):
                        self.upload_bitacora = fields.bitacora
                    elif getattr(fields, "bitacora", None) is not None:
                        self.upload_bitacora = ""
                    if fields.gobierno:
                        self.upload_gobierno = fields.gobierno.strip()
                    elif fields.gobierno is not None:
                        self.upload_gobierno = ""
                    if fields.fecha_emision:
                        self.upload_fecha_emision = fields.fecha_emision
                else:
                    if fields.nombre:
                        self.upload_nombre = fields.nombre
                        self.upload_asunto = fields.nombre
                    elif fields.nombre is not None:
                        self.upload_nombre = ""
                        self.upload_asunto = ""
                    if fields.registro:
                        self.upload_registro = fields.registro
                    elif fields.registro is not None:
                        self.upload_registro = ""
                    if fields.condicionantes:
                        self.upload_condicionantes = "\n".join(fields.condicionantes)
                    else:
                        self.upload_condicionantes = ""
                    if fields.fecha_emision:
                        self.upload_fecha_emision = fields.fecha_emision
                    if fields.vigencia:
                        self.upload_vigencia = fields.vigencia
                    if scope_key not in {"municipal", "municipio"}:
                        if fields.numero:
                            self.upload_numero = fields.numero
                        if fields.gobierno:
                            self.upload_gobierno = fields.gobierno.strip()
                self.upload_extract_status = "Campos extraidos del PDF."
                self.upload_extract_loading = False
                self.upload_textract_lines = lines
                self.upload_fields_pages = pages
                self.upload_field_boxes = field_boxes
                self.upload_highlight_boxes = []
                self.upload_highlight_field = ""
                if self.upload_fields_upload_started_at is not None:
                    fields_elapsed = time.perf_counter() - self.upload_fields_upload_started_at
                    print(
                        "[timing] fields written",
                        f"{fields_elapsed:.2f}s after permit upload",
                    )
                    self.upload_fields_upload_started_at = None
        finally:
            if cleanup_path:
                cleanup_path.unlink(missing_ok=True)

    def set_upload_use_extraction(self, value: bool) -> None:
        self.upload_use_extraction = value
        if not value:
            self.upload_extract_error = ""
            self.upload_extract_status = ""
            self.upload_extract_loading = False
            self.upload_highlight_boxes = []
            self.upload_highlight_field = ""

    def handle_extra_upload(self, files: list[rx.UploadFile]) -> None:
        original_name = ""
        if files and files[0].name:
            original_name = Path(files[0].name).name
        self.upload_is_busy = True
        self.upload_save_success = ""
        self.upload_save_success_token = ""
        yield
        saved_files = self._save_uploads(files)
        self.upload_is_busy = False
        if not saved_files:
            return
        self.upload_extra_pdfs = [saved_files[0]]
        if original_name and not self.upload_extra_pdf_label.strip():
            self.upload_extra_pdf_label = original_name

    def handle_permit_attachment_upload(self, files: list[rx.UploadFile]) -> None:
        self.permit_attachment_error = ""
        original_name = ""
        if files and files[0].name:
            original_name = Path(files[0].name).name
        self.permit_attachment_uploading = True
        yield
        saved_files = self._save_uploads(files)
        self.permit_attachment_uploading = False
        if not saved_files:
            self.permit_attachment_error = "Selecciona un archivo."
            return
        if self.permit_attachment_file:
            delete_pdf_key(self.permit_attachment_file, rx.get_upload_dir())
        self.permit_attachment_file = saved_files[0]
        if original_name and not self.permit_attachment_name.strip():
            self.permit_attachment_name = original_name

    def save_permit_attachment(self) -> None:
        self._ensure_db()
        self.permit_attachment_error = ""
        name = self.permit_attachment_name.strip()
        if not name:
            self.permit_attachment_error = "Nombre requerido."
            return
        if not self.selected_cedis or self.selected_permit_id is None:
            self.permit_attachment_error = "Selecciona un permiso."
            return
        if not self.permit_attachment_file:
            self.permit_attachment_error = "Selecciona un archivo."
            return
        comment = self.permit_attachment_comment.strip()
        with get_session() as session:
            permit_row = (
                session.execute(
                    select(PermitModel).where(
                        PermitModel.id == self.selected_permit_id
                    )
                )
                .scalars()
                .first()
            )
            if not permit_row:
                self.permit_attachment_error = "Permiso no encontrado."
                return
            current_max = (
                session.execute(
                    select(func.max(PermitPdf.order_index)).where(
                        PermitPdf.permit_id == permit_row.id
                    )
                )
                .scalars()
                .first()
            )
            next_order = (current_max if current_max is not None else -1) + 1
            session.add(
                PermitPdf(
                    permit_id=permit_row.id,
                    s3_key=self.permit_attachment_file,
                    label=name,
                    kind="extra_final",
                    comment=comment,
                    order_index=next_order,
                )
            )
        self.permit_attachment_name = ""
        self.permit_attachment_comment = ""
        self.permit_attachment_error = ""
        self.permit_attachment_file = ""
        self.permit_attachment_open = False
        self._load_permits_cache()
        self._refresh_selected_permit()

    def add_manual_permit(self) -> None:
        self._ensure_db()
        self.new_permit_error = ""
        if not self.current_user_id:
            self.new_permit_error = "Inicia sesión para guardar el permiso."
            return
        nombre = self.new_permit_name.strip()
        if not nombre:
            self.new_permit_error = "Nombre requerido."
            return
        if not self.selected_cedis:
            self.new_permit_error = "Selecciona un CEDIS."
            return
        with get_session() as session:
            cedis_row = (
                session.execute(select(Cedis).where(Cedis.name == self.selected_cedis))
                .scalars()
                .first()
            )
            if not cedis_row:
                self.new_permit_error = "CEDIS no encontrado."
                return
            current_max = (
                session.execute(
                    select(func.max(PermitModel.sort_order)).where(
                        PermitModel.cedis_id == cedis_row.id
                    )
                )
                .scalars()
                .first()
            )
            next_order = (current_max if current_max is not None else -1) + 1
            numero = f"MANUAL-{uuid4().hex[:8]}"
            permit_row = PermitModel(
                cedis_id=cedis_row.id,
                nombre=nombre,
                asunto=nombre,
                registro="",
                gobierno="",
                numero=numero,
                permit_scope="Estatal",
                nra="",
                bitacora="",
                created_by_id=self.current_user_id,
                fecha_emision=None,
                vigencia=None,
                sort_order=next_order,
            )
            session.add(permit_row)
            session.flush()
            permit_id = permit_row.id
        self.new_permit_open = False
        self.reset_new_permit_form()
        self.new_permit_id = permit_id
        self._load_permits_cache()
        if self.selected_cedis:
            self.permit_rows = self.permits_by_cedis_all.get(self.selected_cedis, [])
            self.cedis_permits = str(len(self.permit_rows))
            if permit_id is not None:
                self.select_permit(permit_id)

    def show_upload_step_one(self) -> None:
        self.upload_step = 1

    def show_upload_step_two(self) -> None:
        self.upload_step = 2

    def show_upload_step_three(self) -> None:
        self.upload_step = 3

    def show_upload_step_two_back(self) -> None:
        if self.upload_extra_after_step == 1 and self.upload_extra_pdfs:
            self.upload_step = 4
            return
        self.upload_step = 1

    def show_upload_step_three_back(self) -> None:
        if self.upload_extra_after_step == 2 and self.upload_extra_pdfs:
            self.upload_step = 4
            return
        self.upload_step = 2

    def start_extra_step(self, after_step: int) -> None:
        if self.upload_extra_pdfs and self.upload_extra_after_step in (1, 2, 3):
            after_step = self.upload_extra_after_step
        if after_step not in (1, 2, 3):
            after_step = 1
        self.upload_extra_after_step = after_step
        self.upload_save_error = ""
        self.upload_save_success = ""
        self.upload_save_success_token = ""
        self.upload_step = 4

    def show_upload_extra_prev(self) -> None:
        if self.upload_extra_after_step in (1, 2, 3):
            self.upload_step = self.upload_extra_after_step

    def show_upload_extra_next(self) -> None:
        if self.upload_extra_after_step == 1:
            self.upload_step = 2
        elif self.upload_extra_after_step == 2:
            self.upload_step = 3
        elif self.upload_extra_after_step == 3:
            self.upload_step = 3

    def save_upload_extra_pdf(self) -> None:
        self._ensure_db()
        self.upload_save_error = ""
        self.upload_save_success = ""
        self.upload_save_success_token = ""
        if self.selected_permit_id is None:
            self.upload_save_error = "Selecciona un permiso en CEDIS."
            return
        if not self.upload_extra_pdfs:
            self.upload_save_error = "Selecciona un archivo."
            return
        file_key = self.upload_extra_pdfs[0]
        if not file_key:
            self.upload_save_error = "Selecciona un archivo."
            return
        after_step = self.upload_extra_after_step or 2
        if after_step not in (1, 2, 3):
            after_step = 2
        self.upload_extra_after_step = after_step
        order_index = 10 + after_step
        comment = self.upload_extra_pdf_comment.strip()
        label = self.upload_extra_pdf_label.strip() or "Archivo extra"
        with get_session() as session:
            permit_row = (
                session.execute(
                    select(PermitModel).where(
                        PermitModel.id == self.selected_permit_id
                    )
                )
                .scalars()
                .first()
            )
            if not permit_row:
                self.upload_save_error = "Permiso no encontrado."
                return
            if permit_row.created_by_id is None and self.current_user_id:
                permit_row.created_by_id = self.current_user_id
            pdf_row = (
                session.execute(
                    select(PermitPdf).where(
                        PermitPdf.permit_id == permit_row.id,
                        PermitPdf.kind == "extra",
                    )
                )
                .scalars()
                .first()
            )
            if pdf_row:
                pdf_row.s3_key = file_key
                pdf_row.label = label
                pdf_row.comment = comment
                pdf_row.order_index = order_index
            else:
                session.add(
                    PermitPdf(
                        permit_id=permit_row.id,
                        s3_key=file_key,
                        label=label,
                        kind="extra",
                        comment=comment,
                        order_index=order_index,
                    )
                )
            saved_name = permit_row.nombre
        self._load_permits_cache()
        self._refresh_selected_permit()
        return self._set_upload_save_success(
            self._permit_saved_message(saved_name),
            notify=False,
        )

    def toggle_cedis(self) -> None:
        self.cedis_expanded = not self.cedis_expanded

    def toggle_permit_files_for(self, permit_id: int) -> None:
        self._ensure_db()
        if self.permit_files_expanded and self.selected_permit_id == permit_id:
            self.permit_files_expanded = False
            return
        self.select_permit(permit_id)
        self.permit_files_expanded = True

    def reset_permit_attachment_form(self) -> None:
        if self.permit_attachment_file:
            delete_pdf_key(self.permit_attachment_file, rx.get_upload_dir())
            self.permit_attachment_file = ""
        self.permit_attachment_name = ""
        self.permit_attachment_comment = ""
        self.permit_attachment_error = ""
        self.permit_attachment_uploading = False

    def select_zona(self, zona: str) -> None:
        self._ensure_db()
        self.replace_mode = False
        self.permit_files_expanded = False
        self.cedis_initializing = True
        self.region_choice_made = True
        selected = (
            zona
            if zona in self.cedis_by_zona
            else (self.zona_locations[0] if self.zona_locations else "")
        )
        self.selected_zona = selected
        cedis_list = self.cedis_by_zona.get(selected, [])
        target_cedis = (
            cedis_list[0] if cedis_list else (self.cedis_locations[0] if self.cedis_locations else "")
        )
        if target_cedis:
            self.select_cedis(target_cedis)

    def select_cedis(self, location: str) -> None:
        self._ensure_db()
        self.replace_mode = False
        self.permit_files_expanded = False
        selected = (
            location
            if location in self.cedis_locations
            else (self.cedis_locations[0] if self.cedis_locations else "")
        )
        if not selected:
            self.selected_cedis = ""
            self._clear_selected_permit()
            return
        self.selected_cedis = selected
        self._refresh_selected_cedis()

    def select_permit(self, permit_id: int) -> None:
        try:
            permit_id = int(permit_id)
        except (TypeError, ValueError):
            return
        for permit in self.permit_rows:
            if permit.get("id") != permit_id:
                continue
            self.selected_permit_id = permit_id
            self.selected_permit = permit["nombre"]
            self.permit_nombre = permit["nombre"]
            self.permit_asunto = permit.get("nombre", "") or permit.get("asunto", "")
            self.permit_registro = permit.get("registro", "")
            condicionantes = permit.get("condicionantes", [])
            responsable = permit.get("responsable", "")
            tasks: list[dict] = []
            texts: list[str] = []
            if isinstance(condicionantes, list):
                for index, item in enumerate(condicionantes):
                    if isinstance(item, dict):
                        text = str(item.get("text", "")).strip()
                        status = item.get("status") or _label_condition_status(None)
                        cond_id = item.get("id")
                    else:
                        text = str(item).strip()
                        status = _label_condition_status(None)
                        cond_id = None
                    if text:
                        texts.append(text)
                    tasks.append(
                        {
                            "id": cond_id,
                            "index": index + 1,
                            "text": text,
                            "status": status,
                            "responsable": responsable or "",
                        }
                    )
            elif condicionantes:
                text_value = str(condicionantes).strip()
                if text_value:
                    texts.append(text_value)
                    tasks.append(
                        {
                            "id": None,
                            "index": 1,
                            "text": text_value,
                            "status": "no_iniciado",
                            "responsable": responsable or "",
                        }
                    )
            self.permit_condicionantes = "\n".join(texts)
            self.permit_condition_tasks = [
                task for task in tasks if task.get("text")
            ]
            self.permit_responsable = responsable or ""
            self.permit_fecha_emision = permit["fecha_emision"]
            self.permit_vigencia = permit["vigencia"]
            self.permit_gobierno = permit["gobierno"]
            self.permit_numero = permit["numero"]
            self.permit_scope = permit.get("permit_scope") or "Estatal"
            self.permit_nra = permit.get("nra", "") or ""
            self.permit_bitacora = permit.get("bitacora", "") or ""
            self.permit_cedis = permit["cedis"]
            self.permit_status = status_from_permit(permit)
            self.permit_pdf_items = permit.get("pdf_items", [])
            break

    def set_condition_status(self, condition_id: int, value: str) -> None:
        self._ensure_db()
        if not condition_id:
            return
        normalized = _normalize_condition_status(value)
        with get_session() as session:
            condition = (
                session.execute(
                    select(PermitCondition).where(PermitCondition.id == condition_id)
                )
                .scalars()
                .first()
            )
            if not condition:
                return
            condition.status = normalized
            if normalized != "completado":
                session.execute(
                    update(PermitModel)
                    .where(PermitModel.id == condition.permit_id)
                    .values(archived=False)
                )
        self._load_permits_cache()
        self._refresh_selected_permit()

    def _permit_comment_for_kind(self, kind: str) -> str:
        for item in self.permit_pdf_items:
            if item.get("kind") == kind:
                return item.get("comment", "")
        return ""

    def _condition_totals(self) -> tuple[int, int]:
        pending = 0
        total = 0
        for permit_list in self.permits_by_cedis_all.values():
            for permit in permit_list:
                items = permit.get("condicionantes", [])
                if isinstance(items, str):
                    items = [items] if items.strip() else []
                if not isinstance(items, list):
                    continue
                for item in items:
                    total += 1
                    status = ""
                    if isinstance(item, dict):
                        status = str(item.get("status") or "")
                    elif item is not None:
                        status = str(item)
                    if _normalize_condition_status(status) != "completado":
                        pending += 1
        return pending, total

    def set_permit_pdf_comment_local(self, pdf_id: int, value: str) -> None:
        updated: list[dict] = []
        for item in self.permit_pdf_items:
            if item.get("id") == pdf_id:
                refreshed = dict(item)
                refreshed["comment"] = value
                updated.append(refreshed)
            else:
                updated.append(item)
        self.permit_pdf_items = updated

    def update_permit_pdf_comment(self, pdf_id: int, comment: str) -> None:
        self._ensure_db()
        cleaned = (comment or "").strip()
        with get_session() as session:
            pdf = (
                session.execute(select(PermitPdf).where(PermitPdf.id == pdf_id))
                .scalars()
                .first()
            )
            if not pdf:
                return
            pdf.comment = cleaned
        self._load_permits_cache()
        self._refresh_selected_permit()

    def remove_permit_pdf(self, pdf_id: int) -> None:
        self._ensure_db()
        key = ""
        with get_session() as session:
            pdf = (
                session.execute(select(PermitPdf).where(PermitPdf.id == pdf_id))
                .scalars()
                .first()
            )
            if not pdf:
                return
            key = pdf.s3_key or ""
            session.delete(pdf)
        if key:
            delete_pdf_key(key, rx.get_upload_dir())
        self._load_permits_cache()
        self._refresh_selected_permit()

    def handle_permit_pdf_upload(self, files: list[rx.UploadFile]) -> None:
        self._ensure_db()
        if not self.selected_cedis or self.selected_permit_id is None:
            return
        saved_files = self._save_uploads(files)
        if not saved_files:
            return
        with get_session() as session:
            permit_row = (
                session.execute(
                    select(PermitModel).where(
                        PermitModel.id == self.selected_permit_id
                    )
                )
                .scalars()
                .first()
            )
            if not permit_row:
                return
            current_max = (
                session.execute(
                    select(func.max(PermitPdf.order_index)).where(
                        PermitPdf.permit_id == permit_row.id
                    )
                )
                .scalars()
                .first()
            )
            extra_count = (
                session.execute(
                    select(func.count(PermitPdf.id)).where(
                        PermitPdf.permit_id == permit_row.id,
                        PermitPdf.kind == "extra",
                    )
                )
                .scalars()
                .first()
            )
            next_order = (current_max if current_max is not None else -1) + 1
            extra_count = extra_count if extra_count is not None else 0
            for index, key in enumerate(saved_files):
                label_index = extra_count + index + 1
                session.add(
                    PermitPdf(
                        permit_id=permit_row.id,
                        s3_key=key,
                        label=f"Archivo extra {label_index}",
                        kind="extra",
                        comment="",
                        order_index=next_order + index,
                    )
                )
        self._load_permits_cache()
        self._refresh_selected_permit()

    def select_global_permit(self, cedis: str, permit_id: int) -> None:
        self._ensure_db()
        self.permit_files_expanded = False
        self.cedis_initializing = True
        if cedis:
            target_zona = self.zona_by_cedis.get(cedis, "")
            if target_zona:
                # Forzamos región seleccionada para saltar la pantalla de elección.
                self.region_choice_made = True
                self.selected_zona = target_zona
        self.select_cedis(cedis)
        self.select_permit(permit_id)

    def start_permit_update(self) -> None:
        self._ensure_db()
        if self.selected_permit_id is None:
            return
        permit_name = self.permit_nombre or ""
        cedis_name = self.selected_cedis or self.permit_cedis
        new_permit_id = None
        with get_session() as session:
            permit_row = (
                session.execute(
                    select(PermitModel).where(
                        PermitModel.id == self.selected_permit_id
                    )
                )
                .scalars()
                .first()
            )
            if not permit_row:
                return
            permit_name = permit_row.nombre or permit_name
            if permit_row.cedis and permit_row.cedis.name:
                cedis_name = permit_row.cedis.name
            permit_row.archived = True
            numero = f"MANUAL-{uuid4().hex[:8]}"
            new_permit = PermitModel(
                cedis_id=permit_row.cedis_id,
                nombre=permit_name,
                asunto=permit_name,
                registro="",
                gobierno="",
                numero=numero,
                permit_scope="Estatal",
                nra="",
                bitacora="",
                created_by_id=self.current_user_id or permit_row.created_by_id,
                fecha_emision=None,
                vigencia=None,
                sort_order=permit_row.sort_order,
            )
            session.add(new_permit)
            session.flush()
            new_permit_id = new_permit.id
        self.replace_mode = False
        self.replace_target_cedis = ""
        self.replace_target_nombre = ""
        self.replace_target_numero = ""
        self.upload_nombre = permit_name
        self.upload_asunto = permit_name
        self.upload_registro = ""
        self.upload_condicionantes = ""
        self.upload_numero = ""
        self.upload_permit_scope = ""
        self.upload_nra = ""
        self.upload_bitacora = ""
        self.upload_primary_pdf_comment = ""
        self.upload_secondary_pdf_comment = ""
        self.upload_fields_pdf_comment = ""
        self.upload_fecha_emision = ""
        self.upload_vigencia = ""
        self.upload_gobierno = ""
        self.upload_cedis = (
            cedis_name
            if cedis_name
            else (self.selected_cedis if self.selected_cedis else "")
        )
        self.upload_primary_pdf = ""
        self.upload_secondary_pdf = ""
        self.upload_fields_pdf = ""
        self.upload_extra_pdfs = []
        self.upload_extra_after_step = 0
        self.upload_extra_pdf_label = ""
        self.upload_extra_pdf_comment = ""
        self.upload_step = 1
        self.upload_extract_error = ""
        self.upload_extract_status = ""
        self.upload_extract_loading = False
        self.upload_save_error = ""
        self._reset_upload_preview_state()
        self._load_permits_cache()
        if cedis_name:
            self.selected_cedis = cedis_name
        if new_permit_id is not None:
            self.selected_permit_id = new_permit_id
            self.new_permit_id = new_permit_id
        self._refresh_selected_permit()
        self.active_page = "cargar-permiso"

    def add_permit(self) -> None:
        self._ensure_db()
        self.upload_save_error = ""
        if not self.current_user_id:
            self.upload_save_error = "Inicia sesión para guardar el permiso."
            return
        scope_key = (self.upload_permit_scope or "Estatal").strip().lower()
        nombre = self.upload_nombre.strip()
        numero = self.upload_numero.strip()
        nra = self.upload_nra.strip()
        bitacora = self.upload_bitacora.strip()
        primary_comment = self.upload_primary_pdf_comment.strip()
        secondary_comment = self.upload_secondary_pdf_comment.strip()
        fields_comment = self.upload_fields_pdf_comment.strip()
        fecha_emision = self.upload_fecha_emision.strip()
        vigencia = self.upload_vigencia.strip()
        gobierno = self.upload_gobierno.strip()
        asunto = self.upload_asunto.strip()
        registro = self.upload_registro.strip()
        condicionantes_raw = self.upload_condicionantes.strip()
        condicionantes = [
            line.strip()
            for line in condicionantes_raw.splitlines()
            if line.strip()
        ]
        cedis = self.upload_cedis if self.upload_cedis else ""
        pdfs = [
            pdf
            for pdf in [
                self.upload_primary_pdf,
                self.upload_secondary_pdf,
                self.upload_fields_pdf,
            ]
            if pdf
        ]
        extra_pdf = self.upload_extra_pdfs[0] if self.upload_extra_pdfs else ""
        required_ok = False
        if scope_key in {"federal", "federacion"}:
            required_ok = bool(nra and bitacora and gobierno and fecha_emision)
        elif scope_key in {"municipal", "municipio"}:
            required_ok = bool(nombre and registro and fecha_emision and vigencia)
        else:
            required_ok = bool(nombre and numero)
        if (
            not required_ok
            or not self.upload_primary_pdf
            or not self.upload_secondary_pdf
            or not self.upload_fields_pdf
        ):
            return
        if not cedis:
            return
        if not nombre:
            if registro:
                nombre = registro
            elif nra:
                nombre = f"Permiso {nra}"
            else:
                nombre = asunto or "Permiso"
        if not asunto:
            asunto = nombre
        pdf_labels = ["Acuse", "Pago de derechos", "Permiso"]
        pdf_kinds = ["primary", "secondary", "fields"]
        fecha_emision_date = self._parse_input_date(fecha_emision)
        vigencia_date = self._parse_input_date(vigencia)
        with get_session() as session:
            if self.replace_mode and self.replace_target_cedis:
                self._delete_permit_db(
                    session,
                    self.replace_target_cedis,
                    self.replace_target_nombre,
                    self.replace_target_numero,
                )
            cedis_row = (
                session.execute(select(Cedis).where(Cedis.name == cedis))
                .scalars()
                .first()
            )
            if not cedis_row:
                return
            current_max = (
                session.execute(
                    select(func.max(PermitModel.sort_order)).where(
                        PermitModel.cedis_id == cedis_row.id
                    )
                )
                .scalars()
                .first()
            )
            next_order = (current_max if current_max is not None else -1) + 1
            permit_row = PermitModel(
                cedis_id=cedis_row.id,
                nombre=nombre,
                asunto=asunto,
                registro=registro,
                gobierno=gobierno,
                numero=numero,
                permit_scope=self.upload_permit_scope,
                nra=nra,
                bitacora=bitacora,
                created_by_id=self.current_user_id,
                fecha_emision=fecha_emision_date,
                vigencia=vigencia_date,
                sort_order=next_order,
            )
            session.add(permit_row)
            session.flush()
            permit_id = permit_row.id
            for pdf_index, key in enumerate(pdfs):
                label = (
                    pdf_labels[pdf_index]
                    if pdf_index < len(pdf_labels)
                    else f"PDF {pdf_index + 1}"
                )
                kind = pdf_kinds[pdf_index] if pdf_index < len(pdf_kinds) else ""
                comment = ""
                if pdf_index == 0:
                    comment = primary_comment
                elif pdf_index == 1:
                    comment = secondary_comment
                elif pdf_index == 2:
                    comment = fields_comment
                session.add(
                    PermitPdf(
                        permit_id=permit_row.id,
                        s3_key=key,
                        label=label,
                        kind=kind,
                        comment=comment,
                        order_index=pdf_index,
                    )
                )
            if extra_pdf:
                after_step = self.upload_extra_after_step or 2
                if after_step not in (1, 2, 3):
                    after_step = 2
                label = self.upload_extra_pdf_label.strip() or "Archivo extra"
                session.add(
                    PermitPdf(
                        permit_id=permit_row.id,
                        s3_key=extra_pdf,
                        label=label,
                        kind="extra",
                        comment=self.upload_extra_pdf_comment.strip(),
                        order_index=10 + after_step,
                    )
                )
            for cond_index, text in enumerate(condicionantes):
                session.add(
                    PermitCondition(
                        permit_id=permit_row.id,
                        text=text,
                        position=cond_index,
                        status="no_iniciado",
                    )
                )
            session.add(
                PermitStatusHistory(
                    permit_id=permit_row.id, status=status_from_vigencia(vigencia_date)
                )
            )
        if self.current_user_email:
            try:
                send_permit_uploaded(
                    self.current_user_email,
                    {
                        "nombre": nombre,
                        "cedis": cedis,
                        "vigencia": vigencia,
                        "numero": numero,
                    },
                )
            except Exception as e:
                print("SES send_permit_uploaded error:", e)
        self._load_permits_cache()
        if self.selected_cedis == cedis:
            self.permit_rows = self.permits_by_cedis_all.get(cedis, [])
            self.cedis_permits = str(len(self.permit_rows))
            if permit_id is not None:
                self.select_permit(permit_id)
        elif self.replace_mode and self.selected_cedis == self.replace_target_cedis:
            self.permit_rows = self.permits_by_cedis_all.get(self.selected_cedis, [])
            self.cedis_permits = str(len(self.permit_rows))
            if self.permit_rows:
                self.select_permit(self.permit_rows[0]["id"])
        else:
            self._refresh_selected_cedis()
        self.upload_nombre = ""
        self.upload_asunto = ""
        self.upload_registro = ""
        self.upload_condicionantes = ""
        self.upload_numero = ""
        self.upload_permit_scope = ""
        self.upload_nra = ""
        self.upload_bitacora = ""
        self.upload_primary_pdf_comment = ""
        self.upload_secondary_pdf_comment = ""
        self.upload_fields_pdf_comment = ""
        self.upload_fecha_emision = ""
        self.upload_vigencia = ""
        self.upload_gobierno = ""
        self.upload_cedis = cedis
        self.upload_primary_pdf = ""
        self.upload_secondary_pdf = ""
        self.upload_fields_pdf = ""
        self.upload_extra_pdfs = []
        self.upload_extra_after_step = 0
        self.upload_extra_pdf_label = ""
        self.upload_extra_pdf_comment = ""
        self.upload_step = 1
        self.upload_extract_error = ""
        self.upload_extract_status = ""
        self.upload_extract_loading = False
        self.upload_save_error = ""
        self.upload_save_success = ""
        self._cleanup_upload_preview_files()
        self._reset_upload_preview_state()
        self.replace_mode = False
        self.replace_target_cedis = ""
        self.replace_target_nombre = ""
        self.replace_target_numero = ""

    def save_upload_step_pdf(self, kind: str) -> None:
        self._ensure_db()
        self.upload_save_error = ""
        self.upload_save_success = ""
        self.upload_save_success_token = ""
        if self.selected_permit_id is None:
            self.upload_save_error = "Selecciona un permiso en CEDIS."
            return
        file_map = {
            "primary": (
                self.upload_primary_pdf,
                "Acuse",
                self.upload_primary_pdf_comment,
                0,
            ),
            "secondary": (
                self.upload_secondary_pdf,
                "Pago de derechos",
                self.upload_secondary_pdf_comment,
                1,
            ),
            "fields": (
                self.upload_fields_pdf,
                "Permiso",
                self.upload_fields_pdf_comment,
                2,
            ),
        }
        if kind not in file_map:
            self.upload_save_error = "Tipo de archivo no valido."
            return
        file_key, label, comment, order_index = file_map[kind]
        if not file_key:
            self.upload_save_error = "Selecciona un archivo."
            return
        with get_session() as session:
            permit_row = (
                session.execute(
                    select(PermitModel).where(
                        PermitModel.id == self.selected_permit_id
                    )
                )
                .scalars()
                .first()
            )
            if not permit_row:
                self.upload_save_error = "Permiso no encontrado."
                return
            pdf_row = (
                session.execute(
                    select(PermitPdf).where(
                        PermitPdf.permit_id == permit_row.id,
                        PermitPdf.kind == kind,
                    )
                )
                .scalars()
                .first()
            )
            if pdf_row:
                pdf_row.s3_key = file_key
                pdf_row.label = label
                pdf_row.comment = comment.strip()
                pdf_row.order_index = order_index
            else:
                session.add(
                    PermitPdf(
                        permit_id=permit_row.id,
                        s3_key=file_key,
                        label=label,
                        kind=kind,
                        comment=comment.strip(),
                        order_index=order_index,
                    )
                )
            saved_name = permit_row.nombre
        self._load_permits_cache()
        self._refresh_selected_permit()
        return self._set_upload_save_success(
            self._permit_saved_message(saved_name),
            notify=kind == "fields",
        )

    def save_primary_and_continue(self) -> None:
        event = self.save_upload_step_pdf("primary")
        if self.upload_save_error:
            return
        self.show_upload_step_two()
        return event

    def save_secondary_and_continue(self) -> None:
        event = self.save_upload_step_pdf("secondary")
        if self.upload_save_error:
            return
        self.show_upload_step_three()
        return event

    def update_current_permit(self) -> None:
        self._ensure_db()
        self.upload_save_error = ""
        self.upload_save_success = ""
        self.upload_save_success_token = ""
        if self.selected_permit_id is None:
            self.upload_save_error = "Selecciona un permiso en CEDIS."
            return
        was_complete = False
        nombre = self.upload_nombre.strip()
        registro = self.upload_registro.strip()
        gobierno = self.upload_gobierno.strip()
        numero = self.upload_numero.strip()
        nra = self.upload_nra.strip()
        bitacora = self.upload_bitacora.strip()
        permit_scope = self.upload_permit_scope
        scope_key = (permit_scope or "Estatal").strip().lower()
        if not nombre:
            if scope_key in {"municipal", "municipio"} and registro:
                nombre = registro
            elif scope_key in {"federal", "federacion"} and nra:
                nombre = f"Permiso {nra}"
        asunto = self.upload_asunto.strip() or nombre
        fecha_emision = self._parse_input_date(self.upload_fecha_emision.strip())
        vigencia = self._parse_input_date(self.upload_vigencia.strip())
        cedis_name = self.upload_cedis.strip() or self.selected_cedis
        condicionantes = [
            line.strip()
            for line in self.upload_condicionantes.splitlines()
            if line.strip()
        ]
        with get_session() as session:
            permit_row = (
                session.execute(
                    select(PermitModel).where(
                        PermitModel.id == self.selected_permit_id
                    )
                )
                .scalars()
                .first()
            )
            if not permit_row:
                self.upload_save_error = "Permiso no encontrado."
                return
            if not self.replace_mode:
                existing_kinds = set(
                    session.execute(
                        select(PermitPdf.kind).where(
                            PermitPdf.permit_id == permit_row.id
                        )
                    )
                    .scalars()
                    .all()
                )
                was_complete = {"primary", "secondary", "fields"}.issubset(
                    existing_kinds
                )
            target_permit_id = permit_row.id
            target_sort_order = permit_row.sort_order
            target_created_by = permit_row.created_by_id
            if cedis_name and (
                not permit_row.cedis or permit_row.cedis.name != cedis_name
            ):
                cedis_row = (
                    session.execute(select(Cedis).where(Cedis.name == cedis_name))
                    .scalars()
                    .first()
                )
                if not cedis_row:
                    self.upload_save_error = "CEDIS no encontrado."
                    return
                cedis_id = cedis_row.id
            else:
                cedis_id = permit_row.cedis_id
            if self.replace_mode:
                permit_row.archived = True
                new_permit = PermitModel(
                    cedis_id=cedis_id,
                    nombre=nombre or permit_row.nombre,
                    asunto=asunto or permit_row.asunto or (nombre or permit_row.nombre),
                    registro=registro or permit_row.registro,
                    gobierno=gobierno or permit_row.gobierno,
                    numero=numero or permit_row.numero,
                    permit_scope=permit_scope or permit_row.permit_scope,
                    nra=nra or permit_row.nra,
                    bitacora=bitacora or permit_row.bitacora,
                    fecha_emision=fecha_emision or permit_row.fecha_emision,
                    vigencia=vigencia or permit_row.vigencia,
                    created_by_id=self.current_user_id or target_created_by,
                    sort_order=target_sort_order,
                )
                session.add(new_permit)
                session.flush()
                target_permit_id = new_permit.id
            else:
                if cedis_id != permit_row.cedis_id:
                    permit_row.cedis_id = cedis_id
                permit_row.permit_scope = permit_scope or permit_row.permit_scope
                if permit_row.created_by_id is None and self.current_user_id:
                    permit_row.created_by_id = self.current_user_id
                if nombre:
                    permit_row.nombre = nombre
                if asunto:
                    permit_row.asunto = asunto
                if registro:
                    permit_row.registro = registro
                if gobierno:
                    permit_row.gobierno = gobierno
                if numero:
                    permit_row.numero = numero
                if nra:
                    permit_row.nra = nra
                if bitacora:
                    permit_row.bitacora = bitacora
                if fecha_emision:
                    permit_row.fecha_emision = fecha_emision
                if vigencia:
                    permit_row.vigencia = vigencia
            for kind, file_key, label, comment, order_index in [
                ("primary", self.upload_primary_pdf, "Acuse", self.upload_primary_pdf_comment, 0),
                ("secondary", self.upload_secondary_pdf, "Pago de derechos", self.upload_secondary_pdf_comment, 1),
                ("fields", self.upload_fields_pdf, "Permiso", self.upload_fields_pdf_comment, 2),
            ]:
                if not file_key:
                    continue
                pdf_row = (
                    session.execute(
                        select(PermitPdf).where(
                            PermitPdf.permit_id == target_permit_id,
                            PermitPdf.kind == kind,
                        )
                    )
                    .scalars()
                    .first()
                )
                if pdf_row:
                    pdf_row.s3_key = file_key
                    pdf_row.label = label
                    pdf_row.comment = comment.strip()
                    pdf_row.order_index = order_index
                else:
                    session.add(
                        PermitPdf(
                            permit_id=target_permit_id,
                            s3_key=file_key,
                            label=label,
                            kind=kind,
                            comment=comment.strip(),
                            order_index=order_index,
                        )
                    )
            if self.upload_extra_pdfs:
                file_key = self.upload_extra_pdfs[0]
                if file_key:
                    after_step = self.upload_extra_after_step or 2
                    if after_step not in (1, 2, 3):
                        after_step = 2
                    order_index = 10 + after_step
                    comment = self.upload_extra_pdf_comment.strip()
                    label = self.upload_extra_pdf_label.strip() or "Archivo extra"
                    pdf_row = (
                        session.execute(
                            select(PermitPdf).where(
                                PermitPdf.permit_id == target_permit_id,
                                PermitPdf.kind == "extra",
                            )
                        )
                        .scalars()
                        .first()
                    )
                    if pdf_row:
                        pdf_row.s3_key = file_key
                        pdf_row.label = label
                        pdf_row.comment = comment
                        pdf_row.order_index = order_index
                    else:
                        session.add(
                            PermitPdf(
                                permit_id=target_permit_id,
                                s3_key=file_key,
                                label=label,
                                kind="extra",
                                comment=comment,
                                order_index=order_index,
                            )
                        )
            if condicionantes:
                existing = (
                    session.execute(
                        select(PermitCondition).where(
                            PermitCondition.permit_id == target_permit_id
                        )
                    )
                    .scalars()
                    .all()
                )
                for item in existing:
                    session.delete(item)
                for index, text in enumerate(condicionantes):
                    session.add(
                        PermitCondition(
                            permit_id=target_permit_id,
                            text=text,
                            position=index,
                            status="no_iniciado",
                        )
                    )
        now_complete = bool(
            self.upload_primary_pdf and self.upload_secondary_pdf and self.upload_fields_pdf
        )
        if now_complete and not was_complete and self.current_user_email:
            try:
                identifier = numero or nra or registro
                send_permit_uploaded(
                    self.current_user_email,
                    {
                        "nombre": nombre or asunto or permit_row.nombre,
                        "cedis": cedis_name,
                        "vigencia": self.upload_vigencia.strip(),
                        "numero": identifier,
                    },
                )
            except Exception as e:
                print("SES send_permit_uploaded error:", e)
        self.new_permit_id = None
        self.replace_mode = False
        self.replace_target_cedis = ""
        self.replace_target_nombre = ""
        self.replace_target_numero = ""
        self._load_permits_cache()
        if cedis_name:
            self.selected_cedis = cedis_name
        if target_permit_id is not None:
            self.selected_permit_id = target_permit_id
            self._refresh_selected_permit()
        else:
            self._refresh_selected_permit()
        saved_name = nombre or asunto or permit_row.nombre
        return self._set_upload_save_success(
            self._permit_saved_message(saved_name),
            notify=True,
        )

    def clear_upload_save_success(self) -> None:
        self.upload_save_success = ""
        self.upload_save_success_token = ""

    def _set_upload_save_success(self, message: str, *, notify: bool = True):
        token = uuid4().hex
        self.upload_save_success = message
        self.upload_save_success_token = token
        if notify:
            self._push_notification(message)
        return type(self).clear_upload_save_success_later(token)

    @rx.event(background=True)
    async def clear_upload_save_success_later(self, token: str) -> None:
        await asyncio.sleep(5)
        async with self:
            if self.upload_save_success_token != token:
                return
            self.upload_save_success = ""
            self.upload_save_success_token = ""

    def remove_permit(self, permit_id: int) -> None:
        self._ensure_db()
        cedis = self.selected_cedis
        with get_session() as session:
            removed = self._delete_permit_db(session, permit_id)
        if not removed:
            return
        self._load_permits_cache()
        self.permit_rows = self.permits_by_cedis_all.get(cedis, [])
        self.cedis_permits = str(len(self.permit_rows))
        if not self.permit_rows:
            self._clear_selected_permit()
            return
        if not any(
            permit.get("id") == self.selected_permit_id
            for permit in self.permit_rows
        ):
            self.select_permit(self.permit_rows[0]["id"])

    def complete_permit(self, permit_id: int) -> None:
        self._ensure_db()
        with get_session() as session:
            permit_row = (
                session.execute(
                    select(PermitModel).where(PermitModel.id == permit_id)
                )
                .scalars()
                .first()
            )
            if not permit_row:
                return
            permit_row.archived = True
            session.add(
                PermitStatusHistory(
                    permit_id=permit_row.id,
                    status="Completado",
                )
            )
        self._load_permits_cache()

    def start_new_permit(self) -> None:
        self._ensure_db()
        self.replace_mode = False
        self.replace_target_cedis = ""
        self.replace_target_nombre = ""
        self.replace_target_numero = ""
        self.upload_nombre = ""
        self.upload_asunto = ""
        self.upload_registro = ""
        self.upload_condicionantes = ""
        self.upload_numero = ""
        self.upload_permit_scope = ""
        self.upload_nra = ""
        self.upload_bitacora = ""
        self.upload_primary_pdf_comment = ""
        self.upload_secondary_pdf_comment = ""
        self.upload_fields_pdf_comment = ""
        self.upload_fecha_emision = ""
        self.upload_vigencia = ""
        self.upload_gobierno = ""
        self.upload_cedis = (
            self.selected_cedis
            if self.selected_cedis
            else (self.cedis_locations[0] if self.cedis_locations else "")
        )
        self.upload_primary_pdf = ""
        self.upload_secondary_pdf = ""
        self.upload_fields_pdf = ""
        self.upload_extra_pdfs = []
        self.upload_extra_after_step = 0
        self.upload_extra_pdf_label = ""
        self.upload_extra_pdf_comment = ""
        self.upload_step = 1
        self.upload_extract_error = ""
        self.upload_extract_status = ""
        self.upload_extract_loading = False
        self.upload_save_error = ""
        self._reset_upload_preview_state()
        self.active_page = "cargar-permiso"

    def start_permit_flow(self) -> None:
        self._ensure_db()
        self.replace_mode = False
        self.replace_target_cedis = ""
        self.replace_target_nombre = ""
        self.replace_target_numero = ""
        self.upload_nombre = ""
        self.upload_asunto = ""
        self.upload_registro = ""
        self.upload_condicionantes = ""
        self.upload_numero = ""
        self.upload_permit_scope = ""
        self.upload_nra = ""
        self.upload_bitacora = ""
        self.upload_primary_pdf_comment = ""
        self.upload_secondary_pdf_comment = ""
        self.upload_fields_pdf_comment = ""
        self.upload_fecha_emision = ""
        self.upload_vigencia = ""
        self.upload_gobierno = ""
        self.upload_cedis = (
            self.selected_cedis
            if self.selected_cedis
            else (self.cedis_locations[0] if self.cedis_locations else "")
        )
        self.upload_primary_pdf = ""
        self.upload_secondary_pdf = ""
        self.upload_fields_pdf = ""
        self.upload_extra_pdfs = []
        self.upload_extra_after_step = 0
        self.upload_extra_pdf_label = ""
        self.upload_extra_pdf_comment = ""
        self.upload_extract_error = ""
        self.upload_extract_status = ""
        self.upload_extract_loading = False
        self.upload_save_error = ""
        pdf_by_kind = {item.get("kind"): item for item in self.permit_pdf_items}
        primary = pdf_by_kind.get("primary")
        secondary = pdf_by_kind.get("secondary")
        fields = pdf_by_kind.get("fields")
        extra = pdf_by_kind.get("extra")
        if primary:
            self.upload_primary_pdf = primary.get("file", "")
            self.upload_primary_pdf_comment = primary.get("comment", "")
        if secondary:
            self.upload_secondary_pdf = secondary.get("file", "")
            self.upload_secondary_pdf_comment = secondary.get("comment", "")
        if fields:
            self.upload_fields_pdf = fields.get("file", "")
            self.upload_fields_pdf_comment = fields.get("comment", "")
        if extra:
            extra_file = extra.get("file", "")
            if extra_file:
                self.upload_extra_pdfs = [extra_file]
                self.upload_extra_pdf_label = extra.get("label", "")
                self.upload_extra_pdf_comment = extra.get("comment", "")
            order_index = extra.get("order_index")
            if isinstance(order_index, int) and 10 <= order_index <= 13:
                self.upload_extra_after_step = order_index - 10
            elif extra_file:
                self.upload_extra_after_step = 2
        if self.selected_permit_id is not None:
            for permit in self.permit_rows:
                if permit.get("id") == self.selected_permit_id:
                    if self.upload_fields_pdf:
                        self.upload_permit_scope = permit.get("permit_scope") or ""
                        self.upload_nra = permit.get("nra", "") or ""
                        self.upload_bitacora = permit.get("bitacora", "") or ""
                    else:
                        self.upload_permit_scope = ""
                        self.upload_nra = ""
                        self.upload_bitacora = ""
                    break
        if not self.upload_primary_pdf:
            self.upload_step = 1
        elif not self.upload_secondary_pdf:
            self.upload_step = 2
        else:
            self.upload_step = 3
        self._reset_upload_preview_state()
        self.active_page = "cargar-permiso"

    def load_date_range(self, value: str) -> None:
        selected = value if value in DATASETS else DEFAULT_RANGE
        data = DATASETS[selected]
        self.date_range = selected
        self.sales_title = data["kpis"]["sales"]["title"]
        self.sales_value = data["kpis"]["sales"]["value"]
        self.sales_delta = data["kpis"]["sales"]["delta"]
        self.sales_trend = data["kpis"]["sales"]["trend"]
        self.visitors_title = data["kpis"]["visitors"]["title"]
        self.visitors_value = data["kpis"]["visitors"]["value"]
        self.visitors_delta = data["kpis"]["visitors"]["delta"]
        self.visitors_trend = data["kpis"]["visitors"]["trend"]
        self.repeat_title = data["kpis"]["repeat"]["title"]
        self.repeat_value = data["kpis"]["repeat"]["value"]
        self.repeat_delta = data["kpis"]["repeat"]["delta"]
        self.repeat_trend = data["kpis"]["repeat"]["trend"]
        self.sales_over_time = data["sales_over_time"]
        self.visitors_over_time = data["visitors_over_time"]
        self.customers_over_time = data["customers_over_time"]
        self.history = data["history"]

    @rx.var
    def filtered_history(self) -> list[dict]:
        query = self.search_query.strip().lower()
        if not query:
            return self.history
        return [row for row in self.history if query in row["month"].lower()]

    @rx.var
    def filtered_permits(self) -> list[dict]:
        query = self.search_query.strip().lower()
        if not query:
            return self.permit_rows
        return [
            row
            for row in self.permit_rows
            if query in row["nombre"].lower()
            or query in row["gobierno"].lower()
            or query in row["cedis"].lower()
        ]

    @rx.var
    def cedis_options(self) -> list[str]:
        options = self.cedis_by_zona.get(self.selected_zona, [])
        if options:
            return options
        return list(self.cedis_locations)

    @rx.var
    def show_search_results(self) -> bool:
        return self.active_page != "tareas" and bool(self.search_query.strip())

    @rx.var
    def search_placeholder(self) -> str:
        return (
            "Buscar CEDIS..."
            if self.active_page == "tareas"
            else "Buscar permisos..."
        )

    @rx.var
    def has_notifications(self) -> bool:
        return bool(self.notifications)

    @rx.var
    def unread_notifications(self) -> int:
        return sum(1 for item in self.notifications if not item.get("read"))

    @rx.var
    def search_results(self) -> list[dict]:
        query = self.search_query.strip().lower()
        if not query:
            return []
        matches: list[dict] = []
        for permits in self.permits_by_cedis_all.values():
            for permit in permits:
                fields = [
                    permit.get("nombre", ""),
                    permit.get("gobierno", ""),
                    permit.get("cedis", ""),
                    permit.get("numero", ""),
                ]
                if any(query in str(value).lower() for value in fields):
                    matches.append(
                        {
                            "id": permit.get("id"),
                            "nombre": permit["nombre"],
                            "cedis": permit["cedis"],
                            "gobierno": permit.get("gobierno", ""),
                            "numero": permit.get("numero", ""),
                            "status": permit.get("status", ""),
                        }
                    )
        return matches[:8]

    @rx.var
    def has_search_results(self) -> bool:
        return bool(self.search_results)

    @rx.var
    def upload_all_pdfs(self) -> list[str]:
        pdfs: list[str] = []
        if self.upload_primary_pdf:
            pdfs.append(self.upload_primary_pdf)
        if self.upload_secondary_pdf:
            pdfs.append(self.upload_secondary_pdf)
        if self.upload_fields_pdf:
            pdfs.append(self.upload_fields_pdf)
        if self.upload_extra_pdfs:
            pdfs.extend(self.upload_extra_pdfs)
        return pdfs

    @rx.var
    def upload_primary_pdf_url(self) -> str:
        return self._pdf_url(self.upload_primary_pdf)

    @rx.var
    def upload_secondary_pdf_url(self) -> str:
        return self._pdf_url(self.upload_secondary_pdf)

    @rx.var
    def upload_fields_pdf_url(self) -> str:
        return self._pdf_url(self.upload_fields_pdf)

    @rx.var
    def upload_extra_pdf(self) -> str:
        return self.upload_extra_pdfs[0] if self.upload_extra_pdfs else ""

    @rx.var
    def upload_extra_pdf_url(self) -> str:
        return self._pdf_url(self.upload_extra_pdf)

    @rx.var
    def use_s3(self) -> bool:
        return s3_enabled()

    @rx.var
    def upload_primary_pdf_name(self) -> str:
        return self._pdf_name(self.upload_primary_pdf)

    @rx.var
    def upload_secondary_pdf_name(self) -> str:
        return self._pdf_name(self.upload_secondary_pdf)

    @rx.var
    def upload_fields_pdf_name(self) -> str:
        return self._pdf_name(self.upload_fields_pdf)

    @rx.var
    def upload_extra_pdf_name(self) -> str:
        return self._pdf_name(self.upload_extra_pdf)

    @rx.var
    def upload_fields_has_pages(self) -> bool:
        return bool(self.upload_fields_pages)

    @rx.var
    def show_upload_extra_step(self) -> bool:
        return self.upload_step == 4 or bool(self.upload_extra_pdfs)

    @rx.var
    def upload_condicionantes_items(self) -> list[dict]:
        lines = self.upload_condicionantes.split("\n")
        if not lines:
            lines = [""]
        return [
            {"index": index, "label": str(index + 1), "text": line}
            for index, line in enumerate(lines)
        ]

    @rx.var
    def upload_pdfs_label(self) -> str:
        pdfs: list[str] = []
        if self.upload_fields_pdf:
            pdfs.append(self._pdf_name(self.upload_fields_pdf))
        if self.upload_extra_pdfs:
            pdfs.extend(self._pdf_name(pdf) for pdf in self.upload_extra_pdfs)
        if not pdfs:
            return "Sin PDF"
        return ", ".join(pdfs)

    @rx.var
    def upload_preview_file(self) -> str:
        if self.upload_fields_pdf:
            return self.upload_fields_pdf
        if self.upload_primary_pdf:
            return self.upload_primary_pdf
        if self.upload_extra_pdfs:
            return self.upload_extra_pdfs[-1]
        return ""

    @rx.var
    def can_save_permit(self) -> bool:
        scope_key = (self.upload_permit_scope or "Estatal").strip().lower()
        if scope_key in {"federal", "federacion"}:
            required_ok = (
                bool(self.upload_nra.strip())
                and bool(self.upload_bitacora.strip())
                and bool(self.upload_gobierno.strip())
                and bool(self.upload_fecha_emision.strip())
            )
        elif scope_key in {"municipal", "municipio"}:
            required_ok = (
                bool(self.upload_nombre.strip())
                and bool(self.upload_registro.strip())
                and bool(self.upload_fecha_emision.strip())
                and bool(self.upload_vigencia.strip())
            )
        else:
            required_ok = bool(self.upload_nombre.strip()) and bool(
                self.upload_numero.strip()
            )
        return (
            self.is_authenticated
            and bool(self.upload_primary_pdf)
            and bool(self.upload_secondary_pdf)
            and bool(self.upload_fields_pdf)
            and required_ok
        )

    @rx.var
    def permits_by_cedis_list(self) -> list[PermitSection]:
        grouped: list[PermitSection] = []
        query = self.search_query.strip().lower()
        filter_cedis = self.active_page == "tareas" and bool(query)
        for cedis, permits in self.permits_by_cedis.items():
            if filter_cedis and query not in cedis.lower():
                continue
            formatted: list[Permit] = []
            for permit in permits:
                status = status_from_permit(permit)
                completed, total = _permit_condition_progress(permit)
                if total:
                    progress_value = round((completed / total) * 100)
                    progress_label = f"{progress_value}% ({completed}/{total})"
                    progress_color = "blue"
                else:
                    progress_value = 0
                    progress_label = "N/A"
                    progress_color = "gray"
                pdfs = permit.get("pdfs", [])
                pdf_labels = ["Acuse", "Pago de derechos", "Permiso"]
                pdf_items: list[dict] = []
                for index, pdf in enumerate(pdfs):
                    label = (
                        pdf_labels[index]
                        if index < len(pdf_labels)
                        else f"PDF {index + 1}"
                    )
                    pdf_items.append(
                        {"file": pdf, "label": label, "url": self._pdf_url(pdf)}
                    )
                numero_raw = permit.get("numero", "")
                numero_display = (
                    ""
                    if status == "Ingresado" and numero_raw.startswith("MANUAL-")
                    else numero_raw
                )
                formatted.append(
                    PermitView(
                        id=permit.get("id", 0),
                        nombre=permit["nombre"],
                        asunto=permit.get("asunto", "") or permit.get("nombre", ""),
                        registro=permit.get("registro", ""),
                        gobierno=permit["gobierno"],
                        fecha_emision=permit["fecha_emision"],
                        vigencia=permit["vigencia"],
                        numero=numero_raw,
                        numero_display=numero_display,
                        responsable=permit.get("responsable", ""),
                        permit_scope=permit.get("permit_scope", ""),
                        nra=permit.get("nra", ""),
                        bitacora=permit.get("bitacora", ""),
                        cedis=permit["cedis"],
                        status=status,
                        progress_value=progress_value,
                        progress_label=progress_label,
                        progress_color=progress_color,
                        pdfs=list(pdfs),
                        pdfs_label="" if pdfs else "Sin PDF",
                        pdf_items=pdf_items,
                    )
                )
            grouped.append(
                PermitSection(
                    cedis=cedis,
                    permits=formatted,
                    count_label=f"{len(formatted)} tareas",
                )
            )
        return grouped

    @rx.var
    def total_permits(self) -> int:
        return sum(len(permits) for permits in self.permits_by_cedis_all.values())

    @rx.var
    def pending_conditions_count(self) -> int:
        pending, _ = self._condition_totals()
        return pending

    @rx.var
    def total_conditions_count(self) -> int:
        _, total = self._condition_totals()
        return total

    @rx.var
    def pending_conditions_label(self) -> str:
        pending, total = self._condition_totals()
        if total == 0:
            return "Sin condicionantes"
        return f"{pending} pendientes de {total}"

    @rx.var
    def ingresado_count(self) -> int:
        permits: list[dict] = []
        for permit_list in self.permits_by_cedis_all.values():
            permits.extend(permit_list)
        counts = _permit_status_counts(permits)
        return counts.get("Ingresado", 0)

    @rx.var
    def ingresado_percent(self) -> int:
        total = self.total_permits
        if total == 0:
            return 0
        return int(round((self.ingresado_count / total) * 100))

    @rx.var
    def ingresado_badge(self) -> str:
        return f"{self.ingresado_percent}%"

    @rx.var
    def ingresado_mix(self) -> list[dict]:
        total = self.total_permits
        ingresado = self.ingresado_count
        counts = {"Ingresado": ingresado, "Otros": max(total - ingresado, 0)}
        palette = {"Ingresado": "#60a5fa", "Otros": "#e2e8f0"}
        order = ["Ingresado", "Otros"]
        return _build_percent_mix(counts, palette, order)

    @rx.var
    def conditions_completion_percent(self) -> int:
        pending, total = self._condition_totals()
        if total == 0:
            return 0
        completed = total - pending
        return int(round((completed / total) * 100))

    @rx.var
    def conditions_completion_badge(self) -> str:
        return f"{self.conditions_completion_percent}%"

    @rx.var
    def condition_status_mix(self) -> list[dict]:
        permits: list[dict] = []
        for permit_list in self.permits_by_cedis_all.values():
            permits.extend(permit_list)
        counts = _condition_status_counts(permits)
        palette = {
            CONDITION_STATUS_LABELS["no_iniciado"]: "#60a5fa",
            CONDITION_STATUS_LABELS["en_proceso"]: "#6366f1",
            CONDITION_STATUS_LABELS["completado"]: "#a855f7",
        }
        order = [
            CONDITION_STATUS_LABELS["no_iniciado"],
            CONDITION_STATUS_LABELS["en_proceso"],
            CONDITION_STATUS_LABELS["completado"],
        ]
        return _build_percent_mix(counts, palette, order)

    @rx.var
    def expiring_soon_count(self) -> int:
        today = datetime.now().date()
        count = 0
        for permit_list in self.permits_by_cedis_all.values():
            for permit in permit_list:
                if status_from_permit(permit) == "Ingresado":
                    continue
                vigencia_date = self._parse_vigencia_date(permit.get("vigencia"))
                if not vigencia_date:
                    continue
                days_remaining = (vigencia_date - today).days
                if 0 <= days_remaining <= 90:
                    count += 1
        return count

    @rx.var
    def expired_count(self) -> int:
        today = datetime.now().date()
        count = 0
        for permit_list in self.permits_by_cedis_all.values():
            for permit in permit_list:
                if status_from_permit(permit) == "Ingresado":
                    continue
                vigencia_date = self._parse_vigencia_date(permit.get("vigencia"))
                if not vigencia_date:
                    continue
                if (vigencia_date - today).days < 0:
                    count += 1
        return count

    @rx.var
    def expiring_risk_total(self) -> int:
        return self.expiring_soon_count + self.expired_count

    @rx.var
    def expiring_risk_percent(self) -> int:
        total = self.total_permits
        if total == 0:
            return 0
        return int(round((self.expiring_risk_total / total) * 100))

    @rx.var
    def expiring_risk_badge(self) -> str:
        return f"{self.expiring_risk_percent}%"

    @rx.var
    def expiring_bucket_mix(self) -> list[dict]:
        buckets = [
            {"name": "Vencido", "min": -10_000, "max": -1, "color": "#ef4444"},
            {"name": "0-30", "min": 0, "max": 30, "color": "#f97316"},
            {"name": "31-60", "min": 31, "max": 60, "color": "#f59e0b"},
            {"name": "61-90", "min": 61, "max": 90, "color": "#fbbf24"},
        ]
        counts = {bucket["name"]: 0 for bucket in buckets}
        today = datetime.now().date()
        for permit_list in self.permits_by_cedis_all.values():
            for permit in permit_list:
                if status_from_permit(permit) == "Ingresado":
                    continue
                vigencia_date = self._parse_vigencia_date(permit.get("vigencia"))
                if not vigencia_date:
                    continue
                days_remaining = (vigencia_date - today).days
                for bucket in buckets:
                    if bucket["min"] <= days_remaining <= bucket["max"]:
                        counts[bucket["name"]] += 1
                        break
        palette = {bucket["name"]: bucket["color"] for bucket in buckets}
        order = [bucket["name"] for bucket in buckets]
        return _build_percent_mix(counts, palette, order)

    @rx.var
    def permit_status_mix(self) -> list[dict]:
        permits: list[dict] = []
        for permit_list in self.permits_by_cedis_all.values():
            permits.extend(permit_list)
        counts = _permit_status_counts_with_missing(permits, self._parse_vigencia_date)
        counts = _strip_ingresado(counts)
        palette = {
            "Vigente": "#22c55e",
            "Por vencer": "#f59e0b",
            "Vencido": "#ef4444",
            "Sin fecha": "#94a3b8",
        }
        order = ["Vigente", "Por vencer", "Vencido", "Sin fecha"]
        return _build_percent_mix(counts, palette, order)

    @rx.var
    def vigente_percent(self) -> int:
        permits: list[dict] = []
        for permit_list in self.permits_by_cedis_all.values():
            permits.extend(permit_list)
        counts = _permit_status_counts_with_missing(permits, self._parse_vigencia_date)
        counts = _strip_ingresado(counts)
        total = sum(counts.values())
        if total == 0:
            return 0
        return int(round((counts.get("Vigente", 0) / total) * 100))

    @rx.var
    def vigente_badge(self) -> str:
        return f"{self.vigente_percent}%"

    @rx.var
    def expiration_trend(self) -> list[dict]:
        today = datetime.now().date()
        start = date(today.year, today.month, 1)
        buckets: list[dict] = []
        for offset in range(12):
            month_index = (start.month - 1) + offset
            year = start.year + (month_index // 12)
            month = (month_index % 12) + 1
            key = f"{year}-{month:02d}"
            label = f"{MONTH_LABELS[month - 1]}"
            buckets.append({"key": key, "month": label, "value": 0})
        bucket_map = {bucket["key"]: bucket for bucket in buckets}
        for permit_list in self.permits_by_cedis_all.values():
            for permit in permit_list:
                if status_from_permit(permit) == "Ingresado":
                    continue
                vigencia_date = self._parse_vigencia_date(permit.get("vigencia"))
                if not vigencia_date:
                    continue
                key = f"{vigencia_date.year}-{vigencia_date.month:02d}"
                if key in bucket_map:
                    bucket_map[key]["value"] += 1
        return [{"month": bucket["month"], "value": bucket["value"]} for bucket in buckets]

    @rx.var
    def expiration_trend_years(self) -> str:
        today = datetime.now().date()
        start = date(today.year, today.month, 1)
        end_month_index = (start.month - 1) + 11
        end_year = start.year + (end_month_index // 12)
        if start.year == end_year:
            return str(start.year)
        return f"{start.year}-{end_year}"

    @rx.var
    def top_risk_cedis(self) -> list[dict]:
        counts: dict[str, dict[str, int]] = {}
        for permit_list in self.permits_by_cedis_all.values():
            for permit in permit_list:
                cedis = permit.get("cedis", "")
                if not cedis:
                    continue
                status = status_from_permit(permit)
                if status not in ("Por vencer", "Vencido"):
                    continue
                zona = self.zona_by_cedis.get(cedis, cedis)
                entry = counts.setdefault(
                    zona, {"por_vencer": 0, "vencido": 0}
                )
                if status == "Por vencer":
                    entry["por_vencer"] += 1
                else:
                    entry["vencido"] += 1
        positions = {
            "VDM": {"x": "26%", "y": "30%"},
            "Valle de Mexico": {"x": "26%", "y": "30%"},
            "Valle de México": {"x": "26%", "y": "30%"},
            "Centro": {"x": "58%", "y": "48%"},
            "Occidente": {"x": "30%", "y": "70%"},
        }
        rows: list[dict] = []
        for zona, values in counts.items():
            total = values["por_vencer"] + values["vencido"]
            ratio = values["vencido"] / total if total else 0
            if ratio >= 0.5:
                color = "#ef4444"
            elif ratio >= 0.25:
                color = "#f59e0b"
            else:
                color = "#3b82f6"
            pos = positions.get(zona, {"x": "50%", "y": "50%"})
            rows.append(
                {
                    "zona": zona,
                    "por_vencer": values["por_vencer"],
                    "vencido": values["vencido"],
                    "total": total,
                    "x": pos["x"],
                    "y": pos["y"],
                    "color": color,
                }
            )
        max_total = max((row["total"] for row in rows), default=1)
        for row in rows:
            ratio = row["total"] / max_total if max_total else 0
            size = int(70 + (120 - 70) * ratio)
            row["size"] = f"{size}px"
        rows.sort(key=lambda row: row["total"], reverse=True)
        return rows

    @rx.var
    def has_top_risk_cedis(self) -> bool:
        return bool(self.top_risk_cedis)

    @rx.var
    def risk_permits_total(self) -> int:
        return sum(row["total"] for row in self.top_risk_cedis)

    @rx.var
    def region_risk_spider(self) -> list[dict]:
        counts: dict[str, dict[str, int]] = {
            zona: {"total": 0, "vencido": 0} for zona in self.zona_locations
        }
        for permit_list in self.permits_by_cedis_all.values():
            for permit in permit_list:
                cedis = permit.get("cedis", "")
                if not cedis:
                    continue
                zona = self.zona_by_cedis.get(cedis, "")
                if not zona:
                    continue
                entry = counts.setdefault(zona, {"total": 0, "vencido": 0})
                entry["total"] += 1
                if status_from_permit(permit) == "Vencido":
                    entry["vencido"] += 1
        rows: list[dict] = []
        for zona, values in counts.items():
            total = values["total"]
            vencido = values["vencido"]
            percent = int(round((vencido / total) * 100)) if total else 0
            rows.append(
                {
                    "region": zona,
                    "vencido_pct": percent,
                    "vencido": vencido,
                    "total": total,
                }
            )
        return rows

    @rx.var
    def compliance_histogram(self) -> list[dict]:
        buckets = [
            {"range": "0-25%", "min": 0, "max": 25, "value": 0},
            {"range": "26-50%", "min": 26, "max": 50, "value": 0},
            {"range": "51-75%", "min": 51, "max": 75, "value": 0},
            {"range": "76-100%", "min": 76, "max": 100, "value": 0},
        ]
        for permit_list in self.permits_by_cedis_all.values():
            for permit in permit_list:
                completed, total = _permit_condition_progress(permit)
                if total == 0:
                    continue
                percent = int(round((completed / total) * 100))
                for bucket in buckets:
                    if bucket["min"] <= percent <= bucket["max"]:
                        bucket["value"] += 1
                        break
        return [{"range": item["range"], "value": item["value"]} for item in buckets]

    @rx.var
    def compliance_histogram_total(self) -> int:
        return sum(item["value"] for item in self.compliance_histogram)

    @rx.var
    def permit_mix(self) -> list[dict]:
        counts = {"Vencido": 0, "Por vencer": 0, "Vigente": 0}
        for permit_list in self.permits_by_cedis_all.values():
            for permit in permit_list:
                status = status_from_permit(permit)
                if status == "Ingresado":
                    continue
                if status not in counts:
                    continue
                counts[status] += 1
        palette = {
            "Vigente": "#c4b5fd",
            "Por vencer": "#a78bfa",
            "Vencido": "#8b5cf6",
        }
        order = ["Vigente", "Por vencer", "Vencido"]
        total = sum(counts.values())
        items: list[dict] = []
        for name in order:
            value = counts[name]
            if total:
                percent = (value / total) * 100
                percent_label = (
                    f"{percent:.1f}%"
                    if abs(percent - round(percent)) > 0.05
                    else f"{int(round(percent))}%"
                )
            else:
                percent = 0
                percent_label = "0%"
            items.append(
                {
                    "name": name,
                    "value": value,
                    "color": palette[name],
                    "percent": percent,
                    "percent_label": percent_label,
                }
            )
        return items

    @rx.var
    def permit_names(self) -> list[str]:
        return [permit["nombre"] for permit in self.permit_rows]

    @rx.var
    def visible_permit_rows(self) -> list[dict]:
        if (
            self.cedis_initializing
            or not self.permit_files_expanded
            or self.selected_permit_id is None
        ):
            return self.permit_rows
        for permit in self.permit_rows:
            if permit.get("id") == self.selected_permit_id:
                return [permit]
        return self.permit_rows

    @rx.var
    def permit_files_count(self) -> str:
        return str(len(self.permit_pdf_items))

    @rx.var
    def permit_attachment_ready(self) -> bool:
        return bool(
            self.permit_attachment_name.strip()
            and self.permit_attachment_file
            and self.selected_cedis
            and self.selected_permit_id is not None
        )

    @rx.var
    def is_new_permit_selected(self) -> bool:
        return bool(
            self.new_permit_id is not None
            and self.selected_permit_id == self.new_permit_id
        )

    @rx.var
    def permit_flow_started(self) -> bool:
        return any(
            item.get("kind") in ("primary", "secondary", "fields")
            for item in self.permit_pdf_items
        )

    @rx.var
    def permit_flow_completed(self) -> bool:
        kinds = {item.get("kind") for item in self.permit_pdf_items}
        return {"primary", "secondary", "fields"}.issubset(kinds)

    @rx.var
    def permit_flow_label(self) -> str:
        return "Continuar Trámite" if self.permit_flow_started else "Iniciar Trámite"

    @rx.var
    def cedis_conditions_progress_percent(self) -> int:
        completed, total = _condition_counts(self.permit_rows)
        if total == 0:
            return 0
        return int(round((completed / total) * 100))

    @rx.var
    def cedis_conditions_progress_label(self) -> str:
        completed, total = _condition_counts(self.permit_rows)
        if total == 0:
            return "Sin condicionantes"
        return f"{completed}/{total} completadas"

    @rx.var
    def cedis_permit_status_total(self) -> int:
        counts = _permit_status_counts(self.permit_rows)
        return sum(counts.values())

    @rx.var
    def cedis_permit_status_mix(self) -> list[dict]:
        counts = _strip_ingresado(_permit_status_counts(self.permit_rows))
        total = sum(counts.values())
        palette = {
            "Vencido": "#dc2626",
            "Por vencer": "#f59e0b",
            "Vigente": "#16a34a",
        }
        order = ["Vencido", "Por vencer", "Vigente"]
        mix: list[dict] = []
        for name in order:
            count = counts.get(name, 0)
            ratio = (count / total) if total else 0.0
            percent = int(round(ratio * 100))
            mix.append(
                {
                    "name": name,
                    "value": percent,
                    "color": palette[name],
                    "label": f"{name} {percent}%",
                    "width": f"{ratio * 100:.2f}%",
                }
            )
        return mix

    @rx.var
    def permit_condicionantes_items(self) -> list[dict]:
        return list(self.permit_condition_tasks)

    @rx.var
    def has_permit_condicionantes(self) -> bool:
        return bool(self.permit_condition_tasks)

    @rx.var
    def has_permit_history(self) -> bool:
        return bool(self.permit_history_rows)

    @rx.var
    def permit_history_items(self) -> list[PermitView]:
        rows: list[PermitView] = []
        for permit in self.permit_history_rows:
            pdfs = list(permit.get("pdfs", []))
            pdf_items = list(permit.get("pdf_items", []))
            rows.append(
                PermitView(
                    id=permit.get("id", 0),
                    nombre=permit.get("nombre", ""),
                    asunto=permit.get("asunto", "") or permit.get("nombre", ""),
                    registro=permit.get("registro", ""),
                    gobierno=permit.get("gobierno", ""),
                    fecha_emision=permit.get("fecha_emision", ""),
                    vigencia=permit.get("vigencia", ""),
                    numero=permit.get("numero", ""),
                    responsable=permit.get("responsable", ""),
                    cedis=permit.get("cedis", ""),
                    status=permit.get("status", ""),
                    zona=permit.get("zona", ""),
                    pdfs=pdfs,
                    pdfs_label="" if pdfs else "Sin archivos",
                    pdf_items=pdf_items,
                )
            )
        return rows

    @rx.var
    def history_zona_options(self) -> list[str]:
        return ["Todos", *self.zona_locations]

    @rx.var
    def history_cedis_options(self) -> list[str]:
        if self.history_filter_zona == "Todos":
            return ["Todos", *self.cedis_locations]
        cedis_list = self.cedis_by_zona.get(self.history_filter_zona, [])
        return ["Todos", *cedis_list]

    @rx.var
    def history_responsable_options(self) -> list[str]:
        items = {
            permit.get("responsable", "").strip()
            for permit in self.permit_history_rows
        }
        options = sorted([item for item in items if item])
        return ["Todos", *options]

    @rx.var
    def filtered_permit_history_items(self) -> list[PermitView]:
        query = self.history_query.strip().lower()
        filtered: list[PermitView] = []
        for permit in self.permit_history_items:
            if self.history_filter_zona != "Todos" and permit.zona != self.history_filter_zona:
                continue
            if self.history_filter_cedis != "Todos" and permit.cedis != self.history_filter_cedis:
                continue
            if (
                self.history_filter_responsable != "Todos"
                and permit.responsable != self.history_filter_responsable
            ):
                continue
            if query:
                haystack = " ".join(
                    [
                        permit.nombre,
                        permit.numero,
                        permit.cedis,
                        permit.gobierno,
                        permit.zona,
                        permit.responsable,
                    ]
                ).lower()
                if query not in haystack:
                    continue
            filtered.append(permit)
        return filtered

    @rx.var
    def has_filtered_permit_history(self) -> bool:
        return bool(self.filtered_permit_history_items)

    @rx.var
    def expiring_permits(self) -> list[dict]:
        permits: list[dict] = []
        for permit_list in self.permits_by_cedis_all.values():
            for permit in permit_list:
                if status_from_permit(permit) == "Ingresado":
                    continue
                updated = dict(permit)
                updated["status"] = status_from_permit(permit)
                updated["zona"] = self.zona_by_cedis.get(permit.get("cedis", ""), "")
                permits.append(updated)

        def parse_date(value: str | date | None) -> datetime:
            if isinstance(value, date):
                return datetime.combine(value, datetime.min.time())
            parsed = _parse_date_string(value or "")
            if parsed:
                return datetime.combine(parsed, datetime.min.time())
            return datetime.max

        permits.sort(key=lambda permit: parse_date(permit.get("vigencia", "")))
        return permits[:5]
