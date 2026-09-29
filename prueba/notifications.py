"""Helpers para notificaciones por correo usando AWS SES."""

import os
from typing import Any, Dict

import boto3
from botocore.config import Config

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
SES_FROM_EMAIL = os.environ.get("SES_FROM_EMAIL")

_ses_config = Config(
    connect_timeout=5,
    read_timeout=5,
    retries={"max_attempts": 1},
)
ses_client = boto3.client("ses", region_name=AWS_REGION, config=_ses_config)


def send_permit_uploaded(to_email: str, permit: Dict[str, Any]) -> None:
    """Envía un correo cuando se carga un permiso."""
    if not to_email or not SES_FROM_EMAIL:
        return

    subject = f"Permiso cargado: {permit.get('nombre', '')}"
    body_lines = [
        f"Se cargó el permiso: {permit.get('nombre', '')}",
        f"CEDIS/Sitio: {permit.get('cedis', '')}",
        f"Vigencia: {permit.get('vigencia', '')}",
        f"Número: {permit.get('numero', '')}",
    ]
    body = "\n".join(body_lines)

    ses_client.send_email(
        Source=SES_FROM_EMAIL,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}},
        },
    )

