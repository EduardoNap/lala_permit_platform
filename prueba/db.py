"""Database setup and seed helpers."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime
from functools import lru_cache
import os

from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.orm import sessionmaker

from .data import (
    CEDIS_BY_ZONA,
    CEDIS_DETAILS_BY_ZONA,
    PERMITS_BY_CEDIS,
    ZONA_LOCATIONS,
)
from .db_models import (
    Base,
    Cedis,
    Notification,
    Permit,
    PermitCondition,
    PermitPdf,
    PermitStatusHistory,
    Zone,
)


def _database_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL is not set.")
    if url.startswith("postgres://"):
        return f"postgresql+psycopg://{url[len('postgres://'):]}"
    if url.startswith("postgresql://") and "+psycopg" not in url and "+psycopg2" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


@lru_cache
def get_engine():
    return create_engine(_database_url(), pool_pre_ping=True)


SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    Base.metadata.create_all(get_engine())
    _ensure_cedis_columns()
    _ensure_permit_columns()
    _ensure_permit_condition_columns()
    _ensure_permit_pdf_columns()


def _ensure_cedis_columns() -> None:
    engine = get_engine()
    inspector = inspect(engine)
    if "cedis" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("cedis")}
    statements: list[str] = []
    if "direccion" not in columns:
        statements.append(
            "ALTER TABLE cedis ADD COLUMN direccion VARCHAR(220) DEFAULT ''"
        )
    if "empleados" not in columns:
        statements.append(
            "ALTER TABLE cedis ADD COLUMN empleados VARCHAR(40) DEFAULT ''"
        )
    if not statements:
        return
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def _ensure_permit_columns() -> None:
    engine = get_engine()
    inspector = inspect(engine)
    if "permits" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("permits")}
    statements: list[str] = []
    if "created_by_id" not in columns:
        statements.append("ALTER TABLE permits ADD COLUMN created_by_id INTEGER")
    if "archived" not in columns:
        statements.append(
            "ALTER TABLE permits ADD COLUMN archived BOOLEAN DEFAULT FALSE"
        )
    if "permit_scope" not in columns:
        statements.append(
            "ALTER TABLE permits ADD COLUMN permit_scope VARCHAR(24) DEFAULT 'Estatal'"
        )
    if "nra" not in columns:
        statements.append("ALTER TABLE permits ADD COLUMN nra VARCHAR(80) DEFAULT ''")
    if "bitacora" not in columns:
        statements.append(
            "ALTER TABLE permits ADD COLUMN bitacora VARCHAR(120) DEFAULT ''"
        )
    if not statements:
        return
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def _ensure_permit_condition_columns() -> None:
    engine = get_engine()
    inspector = inspect(engine)
    if "permit_conditions" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("permit_conditions")}
    if "status" in columns:
        return
    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE permit_conditions ADD COLUMN status VARCHAR(24) "
                "DEFAULT 'no_iniciado'"
            )
        )


def _ensure_permit_pdf_columns() -> None:
    engine = get_engine()
    inspector = inspect(engine)
    if "permit_pdfs" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("permit_pdfs")}
    if "comment" in columns:
        return
    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE permit_pdfs ADD COLUMN comment TEXT DEFAULT ''")
        )


def _parse_date(value: str | None) -> date | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _status_from_vigencia(value: str | date | None) -> str:
    if isinstance(value, date):
        vigencia_date = value
    else:
        vigencia_date = _parse_date(value)
    if not vigencia_date:
        return "Vigente"
    today = datetime.now().date()
    days_remaining = (vigencia_date - today).days
    if days_remaining < 0:
        return "Vencido"
    if days_remaining <= 90:
        return "Por vencer"
    return "Vigente"


def seed_db() -> None:
    with get_session() as session:
        if session.execute(select(Zone.id)).first():
            return

        zones: list[Zone] = []
        for index, name in enumerate(ZONA_LOCATIONS):
            zone = Zone(name=name, sort_order=index)
            session.add(zone)
            zones.append(zone)
        session.flush()
        zone_by_name = {zone.name: zone for zone in zones}

        cedis_by_name: dict[str, Cedis] = {}
        for zona_name in ZONA_LOCATIONS:
            details = CEDIS_DETAILS_BY_ZONA.get(zona_name, {})
            for index, cedis_name in enumerate(CEDIS_BY_ZONA.get(zona_name, [])):
                cedis = Cedis(
                    name=cedis_name,
                    zone_id=zone_by_name[zona_name].id,
                    sort_order=index,
                    status=details.get("status", ""),
                    autoridad=details.get("autoridad", ""),
                    direccion=details.get("direccion", ""),
                    empleados=details.get("empleados", ""),
                    permiso_medio_ambiente_municipal=bool(
                        details.get("permiso_medio_ambiente_municipal")
                    ),
                    permiso_descarga_municipal=bool(
                        details.get("permiso_descarga_municipal")
                    ),
                    equipo_siga=details.get("equipo_siga", ""),
                    capacity=details.get("capacity", ""),
                )
                session.add(cedis)
                cedis_by_name[cedis_name] = cedis
        session.flush()

        pdf_labels = ["Acuse", "Pago de derechos", "Permiso"]
        pdf_kinds = ["primary", "secondary", "fields"]

        for cedis_name, permits in PERMITS_BY_CEDIS.items():
            cedis = cedis_by_name.get(cedis_name)
            if not cedis:
                continue
            for index, permit in enumerate(permits):
                permit_row = Permit(
                    cedis_id=cedis.id,
                    nombre=permit.get("nombre", ""),
                    asunto=permit.get("asunto", "") or permit.get("nombre", ""),
                    registro=permit.get("registro", ""),
                    gobierno=permit.get("gobierno", ""),
                    numero=permit.get("numero", ""),
                    permit_scope="Estatal",
                    fecha_emision=_parse_date(permit.get("fecha_emision", "")),
                    vigencia=_parse_date(permit.get("vigencia", "")),
                    sort_order=index,
                )
                session.add(permit_row)
                session.flush()

                status = _status_from_vigencia(permit.get("vigencia", ""))
                session.add(
                    PermitStatusHistory(permit_id=permit_row.id, status=status)
                )

                for pdf_index, key in enumerate(permit.get("pdfs", [])):
                    label = (
                        pdf_labels[pdf_index]
                        if pdf_index < len(pdf_labels)
                        else f"PDF {pdf_index + 1}"
                    )
                    kind = (
                        pdf_kinds[pdf_index]
                        if pdf_index < len(pdf_kinds)
                        else "extra"
                    )
                    session.add(
                        PermitPdf(
                            permit_id=permit_row.id,
                            s3_key=key,
                            label=label,
                            kind=kind,
                            order_index=pdf_index,
                        )
                    )

                condicionantes = permit.get("condicionantes", [])
                if isinstance(condicionantes, str):
                    condicionantes = [
                        line.strip()
                        for line in condicionantes.splitlines()
                        if line.strip()
                    ]
                if isinstance(condicionantes, list):
                    for cond_index, text in enumerate(condicionantes):
                        if not isinstance(text, str) or not text.strip():
                            continue
                        session.add(
                            PermitCondition(
                                permit_id=permit_row.id,
                                text=text.strip(),
                                position=cond_index,
                            )
                        )
