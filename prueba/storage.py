"""S3 storage helpers for uploaded PDFs."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os
import tempfile

import boto3

DEFAULT_REGION = "us-east-2"


@dataclass(frozen=True)
class S3Config:
    bucket: str
    region: str | None
    prefix: str
    public_base_url: str | None
    endpoint_url: str | None


@lru_cache
def get_s3_config() -> S3Config | None:
    bucket = os.getenv("AWS_S3_BUCKET", "").strip()
    if not bucket:
        return None
    region = os.getenv("AWS_S3_REGION", "").strip() or DEFAULT_REGION
    prefix = os.getenv("AWS_S3_PREFIX", "").strip().strip("/")
    prefix = f"{prefix}/" if prefix else ""
    public_base_url = os.getenv("AWS_S3_PUBLIC_BASE_URL", "").strip() or None
    endpoint_url = os.getenv("AWS_S3_ENDPOINT_URL", "").strip() or None
    return S3Config(
        bucket=bucket,
        region=region or None,
        prefix=prefix,
        public_base_url=public_base_url,
        endpoint_url=endpoint_url,
    )


@lru_cache
def get_s3_client():
    config = get_s3_config()
    if not config:
        return None
    return boto3.client(
        "s3",
        region_name=config.region or None,
        endpoint_url=config.endpoint_url or None,
    )


def s3_enabled() -> bool:
    return get_s3_config() is not None


def build_s3_key(filename: str) -> str:
    config = get_s3_config()
    if not config:
        return filename
    return f"{config.prefix}{filename}"


def _presign_expires() -> int:
    raw = os.getenv("AWS_S3_PRESIGN_EXPIRES", "").strip()
    if not raw:
        return 3600
    try:
        value = int(raw)
    except ValueError:
        return 3600
    return value if value > 0 else 3600


def upload_pdf_bytes(data: bytes, key: str) -> None:
    config = get_s3_config()
    client = get_s3_client()
    if not config or not client:
        raise RuntimeError("S3 is not configured.")
    client.put_object(
        Bucket=config.bucket,
        Key=key,
        Body=data,
        ContentType="application/pdf",
    )


def delete_pdf_key(key: str, upload_dir: Path | None = None) -> None:
    if not key:
        return
    config = get_s3_config()
    if config:
        client = get_s3_client()
        if not client:
            return
        try:
            client.delete_object(Bucket=config.bucket, Key=key)
        except Exception:
            return
        return
    if not upload_dir:
        return
    path = upload_dir / Path(key).name
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except OSError:
        return


def download_s3_to_temp(key: str) -> Path:
    config = get_s3_config()
    client = get_s3_client()
    if not config or not client:
        raise RuntimeError("S3 is not configured.")
    suffix = Path(key).suffix or ".pdf"
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    client.download_file(config.bucket, key, path)
    return Path(path)


def build_public_url(key: str) -> str:
    config = get_s3_config()
    if not config:
        return ""
    base_url = config.public_base_url
    if not base_url:
        if config.region:
            base_url = f"https://{config.bucket}.s3.{config.region}.amazonaws.com"
        else:
            base_url = f"https://{config.bucket}.s3.amazonaws.com"
    return f"{base_url.rstrip('/')}/{key}"


def build_presigned_url(key: str, expires_in: int | None = None) -> str:
    config = get_s3_config()
    client = get_s3_client()
    if not config or not client:
        raise RuntimeError("S3 is not configured.")
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": config.bucket, "Key": key},
        ExpiresIn=expires_in if expires_in is not None else _presign_expires(),
    )


def build_file_url(key: str) -> str:
    if not key:
        return ""
    config = get_s3_config()
    if not config:
        return ""
    if config.public_base_url:
        return build_public_url(key)
    return build_presigned_url(key)
