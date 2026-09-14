from __future__ import annotations

from dataclasses import dataclass, field
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
_NEUTRAL_ID_RE = re.compile(r"^(CASE|REQUEST|SPEC|INVOICE|DELIVERY|CONTROL|DOC)_([0-9]{4})$")
_MAX_ORDINAL = 9999


def _normalize_prefix(prefix: str) -> str:
    if not isinstance(prefix, str):
        raise TypeError("neutral-id prefix must be a string")
    normalized = prefix.strip().upper()
    if normalized not in _ALLOWED_PREFIXES:
        raise ValueError("unsupported neutral-id prefix")
    return normalized


@dataclass
class NeutralIdAllocator:
    """Allocate public IDs from internal counters only.

    The allocator deliberately accepts no caller-supplied ordinal. Public
    sequence numbers therefore come from publication order, not source
    filenames, dates, supplier identities, private hashes, or original
    document numbers.
    """

    _last_by_prefix: dict[str, int] = field(default_factory=dict, init=False, repr=False)

    def allocate(self, prefix: str) -> str:
        normalized = _normalize_prefix(prefix)
        ordinal = self._last_by_prefix.get(normalized, 0) + 1
        if ordinal > _MAX_ORDINAL:
            raise ValueError("neutral-id sequence exhausted")
        self._last_by_prefix[normalized] = ordinal
        return f"{normalized}_{ordinal:04d}"


def _validate_neutral_id(value: str) -> str:
    if not isinstance(value, str) or not _NEUTRAL_ID_RE.fullmatch(value):
        raise ValueError("not a neutral public id")
    return value


def _neutral_id_parts(value: str) -> tuple[str, int]:
    validated = _validate_neutral_id(value)
    match = _NEUTRAL_ID_RE.fullmatch(validated)
    assert match is not None
    return match.group(1), int(match.group(2))
