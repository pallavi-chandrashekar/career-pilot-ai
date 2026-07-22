"""Deterministic upload validation primitives; parsing belongs to Task 004."""

from hashlib import sha256
from pathlib import Path

PDF_MIME = "application/pdf"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def validate_upload(*, content: bytes, filename: str, mime_type: str) -> str:
    """Validate bounded bytes using file signatures, without retaining content in logs."""

    if not content or len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("Document size is invalid.")
    suffix = Path(filename).suffix.casefold()
    if mime_type == PDF_MIME and suffix == ".pdf" and content.startswith(b"%PDF-"):
        return "RESUME"
    if mime_type == DOCX_MIME and suffix == ".docx" and content.startswith(b"PK"):
        return "RESUME"
    raise ValueError("Only valid PDF and DOCX documents are accepted.")


def document_checksum(content: bytes) -> str:
    return sha256(content).hexdigest()
