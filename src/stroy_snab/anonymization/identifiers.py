from __future__ import annotations

import re
from typing import Iterator

_DIGIT_TOKEN_RE = re.compile(r"(?<!\d)\d{10,15}(?!\d)")


def _weighted_mod11_digit(digits: str, coefficients: tuple[int, ...]) -> int:
    return sum(int(char) * coefficient for char, coefficient in zip(digits, coefficients, strict=True)) % 11 % 10


def is_inn(value: str) -> bool:
    if not value.isdigit():
        return False
    if len(value) == 10:
        expected = _weighted_mod11_digit(value[:9], (2, 4, 10, 3, 5, 9, 4, 6, 8))
        return int(value[9]) == expected
    if len(value) == 12:
        digit11 = _weighted_mod11_digit(value[:10], (7, 2, 4, 10, 3, 5, 9, 4, 6, 8))
        digit12 = _weighted_mod11_digit(value[:10] + str(digit11), (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8))
        return int(value[10]) == digit11 and int(value[11]) == digit12
    return False


def is_ogrn(value: str) -> bool:
    if not value.isdigit():
        return False
    if len(value) == 13:
        return int(value[-1]) == int(value[:12]) % 11 % 10
    if len(value) == 15:
        return int(value[-1]) == int(value[:14]) % 13 % 10
    return False


def iter_unlabeled_tax_identifiers(text: str) -> Iterator[str]:
    """Yield identifier kinds only; never return or log matched private values."""

    for match in _DIGIT_TOKEN_RE.finditer(text):
        value = match.group(0)
        if is_inn(value):
            yield "inn_unlabeled"
        elif is_ogrn(value):
            yield "ogrn_unlabeled"
