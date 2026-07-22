"""Synthetic parser coverage; no real candidate documents are used."""

from io import BytesIO

import pytest
from docx import Document as DocxDocument

from careerpilot_api.documents.crypto import ParsedContentCipher
from careerpilot_api.documents.parser import parse_document
from careerpilot_api.documents.service import DOCX_MIME, PDF_MIME


def _pdf_with_text(lines: list[str]) -> bytes:
    content = (
        "BT /F1 12 Tf 72 720 Td " + " ".join(f"({line}) Tj 0 -18 Td" for line in lines) + " ET"
    )
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(content)} >>\nstream\n{content}\nendstream",
    ]
    result = b"%PDF-1.4\n"
    offsets = [0]
    for number, value in enumerate(objects, start=1):
        offsets.append(len(result))
        result += f"{number} 0 obj\n{value}\nendobj\n".encode()
    xref = len(result)
    result += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    result += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:])
    return result + f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()


def _docx_with_text(lines: list[str]) -> bytes:
    document = DocxDocument()
    for line in lines:
        document.add_paragraph(line)
    output = BytesIO()
    document.save(output)
    return output.getvalue()


@pytest.mark.parametrize(
    ("mime_type", "content"),
    [
        (PDF_MIME, _pdf_with_text(["SUMMARY", "Fictional profile", "SKILLS", "Python"])),
        (DOCX_MIME, _docx_with_text(["SUMMARY", "Fictional profile", "SKILLS", "Python"])),
    ],
)
def test_parser_preserves_text_sections_and_line_locations(mime_type: str, content: bytes) -> None:
    result = parse_document(content=content, mime_type=mime_type)

    assert result.text == "SUMMARY\nFictional profile\nSKILLS\nPython"
    assert [
        (section.title, section.start_line, section.end_line) for section in result.sections
    ] == [
        ("SUMMARY", 1, 2),
        ("SKILLS", 3, 4),
    ]


@pytest.mark.parametrize(
    ("mime_type", "content", "message"),
    [
        (PDF_MIME, b"not-a-pdf", "PDF content could not be parsed"),
        (DOCX_MIME, b"not-a-docx", "DOCX content could not be parsed"),
        ("text/plain", b"ignored", "unsupported for parsing"),
    ],
)
def test_parser_rejects_malformed_or_unsupported_content(
    mime_type: str, content: bytes, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        parse_document(content=content, mime_type=mime_type)


def test_parsed_content_cipher_round_trips_without_plaintext_storage() -> None:
    cipher = ParsedContentCipher("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    encrypted = cipher.encrypt("Fictional Candidate")

    assert encrypted != "Fictional Candidate"
    assert cipher.decrypt(encrypted) == "Fictional Candidate"
