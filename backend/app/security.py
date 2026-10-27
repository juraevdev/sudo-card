from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from .config import get_settings


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        scheme, salt, digest_hex = hashed.split("$", 2)
    except ValueError:
        return False
    if scheme != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return hmac.compare_digest(digest.hex(), digest_hex)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": subject, "exp": expire},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_access_token(token: str) -> str | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError:
        return None
    sub = payload.get("sub")
    return sub if isinstance(sub, str) else None


def new_qr_token() -> str:
    """URL-safe opaque token for the QR payload (no PII)."""
    return secrets.token_urlsafe(24)


def build_qr_payload(token: str) -> str:
    settings = get_settings()
    return f"{settings.qr_prefix}.{token}"


def parse_qr_payload(raw: str) -> str | None:
    """Extract the opaque token from a scanned QR string."""
    value = raw.strip()
    settings = get_settings()
    prefix = f"{settings.qr_prefix}."
    if value.startswith(prefix):
        token = value[len(prefix) :]
        return token or None
    # Accept bare token for flexibility during testing.
    if len(value) >= 16 and " " not in value and "{" not in value:
        return value
    return None
