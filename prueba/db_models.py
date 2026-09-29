"""SQLAlchemy models for persisted app data."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    cedis: Mapped[list["Cedis"]] = relationship(
        back_populates="zone", cascade="all, delete-orphan"
    )


class Cedis(Base):
    __tablename__ = "cedis"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    zone_id: Mapped[int] = mapped_column(
        ForeignKey("zones.id", ondelete="CASCADE"), index=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(64), default="")
    autoridad: Mapped[str] = mapped_column(String(180), default="")
    direccion: Mapped[str] = mapped_column(String(220), default="")
    empleados: Mapped[str] = mapped_column(String(40), default="")
    permiso_medio_ambiente_municipal: Mapped[bool] = mapped_column(Boolean, default=False)
    permiso_descarga_municipal: Mapped[bool] = mapped_column(Boolean, default=False)
    equipo_siga: Mapped[str] = mapped_column(String(120), default="")
    capacity: Mapped[str] = mapped_column(String(64), default="")

    zone: Mapped["Zone"] = relationship(back_populates="cedis")
    permits: Mapped[list["Permit"]] = relationship(
        back_populates="cedis", cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120), default="")
    password_hash: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    permits: Mapped[list["Permit"]] = relationship(
        back_populates="created_by", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Permit(Base):
    __tablename__ = "permits"

    id: Mapped[int] = mapped_column(primary_key=True)
    cedis_id: Mapped[int] = mapped_column(
        ForeignKey("cedis.id", ondelete="CASCADE"), index=True
    )
    nombre: Mapped[str] = mapped_column(String(200), index=True)
    asunto: Mapped[str] = mapped_column(String(200), default="")
    registro: Mapped[str] = mapped_column(String(200), default="")
    gobierno: Mapped[str] = mapped_column(String(80), default="")
    numero: Mapped[str] = mapped_column(String(80), index=True)
    permit_scope: Mapped[str] = mapped_column(String(24), default="Estatal")
    nra: Mapped[str] = mapped_column(String(80), default="")
    bitacora: Mapped[str] = mapped_column(String(120), default="")
    fecha_emision: Mapped[date | None] = mapped_column(Date, nullable=True)
    vigencia: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    archived: Mapped[bool] = mapped_column(Boolean, default=False)

    cedis: Mapped["Cedis"] = relationship(back_populates="permits")
    created_by: Mapped["User"] = relationship(back_populates="permits")
    pdfs: Mapped[list["PermitPdf"]] = relationship(
        back_populates="permit", cascade="all, delete-orphan"
    )
    conditions: Mapped[list["PermitCondition"]] = relationship(
        back_populates="permit", cascade="all, delete-orphan"
    )
    statuses: Mapped[list["PermitStatusHistory"]] = relationship(
        back_populates="permit", cascade="all, delete-orphan"
    )


class PermitPdf(Base):
    __tablename__ = "permit_pdfs"

    id: Mapped[int] = mapped_column(primary_key=True)
    permit_id: Mapped[int] = mapped_column(
        ForeignKey("permits.id", ondelete="CASCADE"), index=True
    )
    s3_key: Mapped[str] = mapped_column(String(512))
    label: Mapped[str] = mapped_column(String(120), default="")
    kind: Mapped[str] = mapped_column(String(32), default="")
    comment: Mapped[str] = mapped_column(Text, default="")
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    permit: Mapped["Permit"] = relationship(back_populates="pdfs")


class PermitCondition(Base):
    __tablename__ = "permit_conditions"

    id: Mapped[int] = mapped_column(primary_key=True)
    permit_id: Mapped[int] = mapped_column(
        ForeignKey("permits.id", ondelete="CASCADE"), index=True
    )
    text: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(24), default="no_iniciado")

    permit: Mapped["Permit"] = relationship(back_populates="conditions")


class PermitStatusHistory(Base):
    __tablename__ = "permit_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    permit_id: Mapped[int] = mapped_column(
        ForeignKey("permits.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(32))
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    permit: Mapped["Permit"] = relationship(back_populates="statuses")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    message: Mapped[str] = mapped_column(String(240))
    category: Mapped[str] = mapped_column(String(32), default="success")
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="notifications")
