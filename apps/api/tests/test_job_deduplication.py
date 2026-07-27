from hashlib import sha256


def test_fingerprint_is_stable_for_case_only_changes() -> None:
    assert (
        sha256(b"fictional systems\nrole\npython").hexdigest()
        == sha256("Fictional Systems\nRole\nPython".casefold().encode()).hexdigest()
    )
