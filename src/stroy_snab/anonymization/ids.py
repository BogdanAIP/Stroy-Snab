from __future__ import annotations

import re

_ALLOWED_PREFIXES = {
    "CASE",
    "REQUEST",
    "SPEC",
    "INVOICE",
    "DELIVERY",
    "CONTROL",
    "DOC",
}
_NEUTRAL_ID_RE = re.compile(r"^(CASE|REQUEST|SPEC|INVOICE|DELIVERY|CONTROL|DOC)_[0-9]{4,8}$")


def neutral_id(prefix: str, ordinal: int, *, width: int = 4) -> str:
    """Create a public id from a neutral ordinal only.

    Never derive public ids from a source filename, supplier, date, document number,
    hash of private data, or other reversible source identifier.
    """
    normalized = prefix.strip().upper()
    if normalized not in _ALLOWED_PREFIXES:
        raise ValueError("unsupported neutral-id prefix")
    if ordinal < 1:
        raise ValueError("ordinal must be >= 1")
    if not 4 <= width <= 8:
        raise ValueError("width must be between 4 and 8")
    value = f"{normalized}_{ordinal:0{width}d}"
    return validate_neutral_id(value)


def validate_neutral_id(value: str) -> str:
    if not isinstance(value, str) or not _NEUTRAL_ID_RE.fullmatch(value):
        raise ValueError("not a neutral public id")
    return value
