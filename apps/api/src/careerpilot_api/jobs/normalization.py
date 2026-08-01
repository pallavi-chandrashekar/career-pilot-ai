"""Deterministic extraction of explicit job signals."""

import re


def normalize(description: str) -> dict[str, object]:
    text = description.casefold()
    seniority = next(
        (
            value
            for value in ("intern", "junior", "senior", "staff", "principal")
            if re.search(rf"\b{value}\b", text)
        ),
        None,
    )
    numbers = re.findall(r"\$([0-9]{2,3})[,]?([0-9]{3})?", description)
    compensation = None if not numbers else {"amounts": [int(a + (b or "")) for a, b in numbers]}
    sponsorship = (
        "UNAVAILABLE"
        if "no sponsorship" in text
        else "AVAILABLE"
        if "sponsorship available" in text
        else "UNKNOWN"
    )
    clearance = (
        "NOT_REQUIRED"
        if re.search(r"\b(no|not) (security )?clearance (is )?required\b", text)
        else "REQUIRED"
        if "security clearance" in text or "clearance required" in text
        else "UNKNOWN"
    )
    required = [
        line.strip()
        for line in description.splitlines()
        if re.search(r"required|must have", line, re.I)
    ]
    preferred = [
        line.strip()
        for line in description.splitlines()
        if re.search(r"preferred|nice to have", line, re.I)
    ]
    return {
        "seniority": seniority,
        "compensation": compensation,
        "sponsorship": sponsorship,
        "clearance": clearance,
        "requirements": {"required": required, "preferred": preferred},
    }
