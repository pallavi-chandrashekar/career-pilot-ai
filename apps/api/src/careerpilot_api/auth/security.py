"""Password and signed-token primitives with no sensitive logging."""

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000)
    return f"pbkdf2_sha256$600000${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    algorithm, iterations, salt_hex, digest_hex = encoded.split("$", 3)
    if algorithm != "pbkdf2_sha256":
        return False
    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
    )
    return hmac.compare_digest(candidate.hex(), digest_hex)


def issue_access_token(user_id: UUID, secret: str, minutes: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": int((datetime.now(UTC) + timedelta(minutes=minutes)).timestamp()),
    }
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).rstrip(
        b"="
    )
    signature = hmac.new(secret.encode(), body, hashlib.sha256).digest()
    return f"{body.decode()}.{base64.urlsafe_b64encode(signature).rstrip(b'=').decode()}"


def verify_access_token(token: str, secret: str) -> UUID | None:
    try:
        body, signature = token.split(".", 1)
        expected = (
            base64.urlsafe_b64encode(
                hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest()
            )
            .rstrip(b"=")
            .decode()
        )
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if int(payload["exp"]) <= int(datetime.now(UTC).timestamp()):
            return None
        return UUID(payload["sub"])
    except (KeyError, ValueError, json.JSONDecodeError):
        return None
