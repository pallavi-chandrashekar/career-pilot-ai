import pytest

from careerpilot_api.jobs.url_ingestion import text_from_html, validate_public_url


def test_private_urls_are_rejected() -> None:
    with pytest.raises(ValueError, match="Private network"):
        validate_public_url("http://127.0.0.1/jobs")


def test_html_text_extraction_ignores_scripts() -> None:
    assert (
        text_from_html("<h1>Fictional Role</h1><script>ignore()</script><p>Remote</p>")
        == "Fictional Role Remote"
    )
