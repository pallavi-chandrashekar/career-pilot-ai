"""Bounded, SSRF-conscious public job URL retrieval."""

import ipaddress
import re
from html import unescape
from urllib.parse import urlparse

import httpx


def validate_public_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username:
        raise ValueError("Only public HTTP(S) URLs are permitted.")
    if parsed.hostname.casefold() == "localhost":
        raise ValueError("Private network URLs are not permitted.")
    try:
        if (
            ipaddress.ip_address(parsed.hostname).is_private
            or ipaddress.ip_address(parsed.hostname).is_loopback
        ):
            raise ValueError("Private network URLs are not permitted.")
    except ValueError as error:
        if str(error) == "Private network URLs are not permitted.":
            raise
    return value


def text_from_html(value: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


async def fetch_job_page(url: str) -> tuple[str, str | None]:
    validate_public_url(url)
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url, headers={"User-Agent": "CareerPilotAI/0.1"})
        if response.status_code in {401, 403, 429}:
            raise PermissionError("The page blocked retrieval. Paste the job description instead.")
        response.raise_for_status()
        if "html" not in response.headers.get("content-type", "").casefold():
            raise ValueError(
                "The URL did not return an HTML page. Paste the job description instead."
            )
        text = text_from_html(response.text)
        if not text:
            raise ValueError(
                "No readable job content was found. Paste the job description instead."
            )
        title_match = re.search(r"(?is)<title[^>]*>(.*?)</title>", response.text)
        return text[:100000], unescape(title_match.group(1)).strip() if title_match else None
    except httpx.HTTPError as error:
        raise PermissionError(
            "The page could not be retrieved. Paste the job description instead."
        ) from error
