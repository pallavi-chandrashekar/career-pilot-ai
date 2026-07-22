"""Unit coverage for deterministic document acceptance and storage contracts."""

import pytest

from careerpilot_api.documents.service import (
    DOCX_MIME,
    MAX_UPLOAD_BYTES,
    PDF_MIME,
    document_checksum,
    validate_upload,
)
from careerpilot_api.storage.s3 import S3ObjectStorage


def test_valid_pdf_is_classified_without_parsing_candidate_content() -> None:
    assert (
        validate_upload(
            content=b"%PDF-1.7\\nfictional candidate document",
            filename="resume.pdf",
            mime_type=PDF_MIME,
        )
        == "RESUME"
    )


@pytest.mark.parametrize(
    ("filename", "mime_type", "content"),
    [
        ("resume.docx", DOCX_MIME, b"not-a-zip"),
        ("resume.pdf", PDF_MIME, b"not-a-pdf"),
        ("resume.txt", PDF_MIME, b"%PDF-1.7"),
        ("resume.pdf", "text/plain", b"%PDF-1.7"),
    ],
)
def test_invalid_or_mismatched_documents_are_rejected(
    filename: str, mime_type: str, content: bytes
) -> None:
    with pytest.raises(ValueError, match="Only valid PDF and DOCX"):
        validate_upload(content=content, filename=filename, mime_type=mime_type)


def test_oversized_document_is_rejected() -> None:
    with pytest.raises(ValueError, match="Document size is invalid"):
        validate_upload(
            content=b"%PDF-" + b"0" * MAX_UPLOAD_BYTES,
            filename="resume.pdf",
            mime_type=PDF_MIME,
        )


def test_checksum_is_deterministic() -> None:
    assert document_checksum(b"fictional document") == document_checksum(b"fictional document")
    assert document_checksum(b"fictional document") != document_checksum(b"different document")


class FakeS3Client:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def put_object(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return {}


def test_storage_uses_bucket_and_opaque_key() -> None:
    client = FakeS3Client()
    storage = S3ObjectStorage(client, "documents")

    storage.put_bytes(
        key="users/fictional/documents/opaque-id",
        content=b"%PDF-fictional",
        content_type=PDF_MIME,
    )

    assert client.calls == [
        {
            "Bucket": "documents",
            "Key": "users/fictional/documents/opaque-id",
            "Body": b"%PDF-fictional",
            "ContentType": PDF_MIME,
        }
    ]
