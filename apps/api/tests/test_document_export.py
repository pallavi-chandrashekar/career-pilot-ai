from careerpilot_api.applications.export import render_docx, render_pdf


def test_renders_docx_and_pdf_from_package_content() -> None:
    content = {
        "tailored_resume": ["Built fictional Python services."],
        "cover_letter": "Dear team.",
    }
    assert render_docx(title="Fictional Platform Engineer", content=content).startswith(b"PK")
    assert render_pdf(title="Fictional Platform Engineer", content=content).startswith(b"%PDF-")
