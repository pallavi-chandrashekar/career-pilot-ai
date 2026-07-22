"""Deterministic PDF and DOCX parsing with line-based source locations."""

import re
from dataclasses import dataclass
from io import BytesIO

from docx import Document as DocxDocument
from pypdf import PdfReader

from careerpilot_api.documents.service import DOCX_MIME, PDF_MIME

PARSER_VERSION = "1"
_KNOWN_HEADINGS = {
    "EDUCATION",
    "EXPERIENCE",
    "PROFESSIONAL EXPERIENCE",
    "PROJECTS",
    "SKILLS",
    "SUMMARY",
    "WORK EXPERIENCE",
}


@dataclass(frozen=True)
class ParsedSection:
    title: str
    start_line: int
    end_line: int


@dataclass(frozen=True)
class ParseResult:
    text: str
    sections: tuple[ParsedSection, ...]


def parse_document(*, content: bytes, mime_type: str) -> ParseResult:
    """Extract text without interpreting or logging candidate claims."""

    if mime_type == PDF_MIME:
        lines = _pdf_lines(content)
    elif mime_type == DOCX_MIME:
        lines = _docx_lines(content)
    else:
        raise ValueError("Document type is unsupported for parsing.")
    return ParseResult(text="\n".join(lines), sections=_segment_sections(lines))


def _pdf_lines(content: bytes) -> list[str]:
    try:
        reader = PdfReader(BytesIO(content))
        return _normalise_lines("\n".join(page.extract_text() or "" for page in reader.pages))
    except Exception as error:
        raise ValueError("PDF content could not be parsed.") from error


def _docx_lines(content: bytes) -> list[str]:
    try:
        document = DocxDocument(BytesIO(content))
        return _normalise_lines("\n".join(paragraph.text for paragraph in document.paragraphs))
    except Exception as error:
        raise ValueError("DOCX content could not be parsed.") from error


def _normalise_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _segment_sections(lines: list[str]) -> tuple[ParsedSection, ...]:
    headings = [(index, line) for index, line in enumerate(lines, start=1) if _is_heading(line)]
    if not headings:
        return ()
    sections: list[ParsedSection] = []
    for position, (start_line, title) in enumerate(headings):
        end_line = headings[position + 1][0] - 1 if position + 1 < len(headings) else len(lines)
        sections.append(ParsedSection(title=title, start_line=start_line, end_line=end_line))
    return tuple(sections)


def _is_heading(line: str) -> bool:
    normalized = re.sub(r"\s+", " ", line).strip().upper()
    return normalized in _KNOWN_HEADINGS
