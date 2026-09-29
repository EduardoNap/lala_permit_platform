"""Helpers para autenticación simple."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import os

PBKDF2_ROUNDS = 120_000
SALT_BYTES = 16


def _b64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"))


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Contraseña requerida.")
    salt = os.urandom(SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS
    )
    return f"{_b64encode(salt)}${_b64encode(derived)}"


def verify_password(password: str, stored_hash: str) -> bool:
    if not password or not stored_hash:
        return False
    if "$" not in stored_hash:
        return False
    salt_b64, hash_b64 = stored_hash.split("$", 1)
    try:
        salt = _b64decode(salt_b64)
        expected = _b64decode(hash_b64)
    except (ValueError, binascii.Error):
        return False
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS
    )
    return hmac.compare_digest(derived, expected)
