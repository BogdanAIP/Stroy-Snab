from __future__ import annotations

from stroy_snab.anonymization.identifiers import is_inn, is_ogrn
from stroy_snab.anonymization import scan_text


def test_checksum_valid_unlabeled_inn_is_blocked_without_echoing_value():
    value = "1234567894"
    assert is_inn(value)
    findings = scan_text(f"safe-prefix {value} safe-suffix", forbidden_tokens=[])
    matching = [finding for finding in findings if finding.kind == "inn_unlabeled"]
    assert matching
    assert all(value not in finding.evidence for finding in matching)


def test_checksum_valid_12_digit_inn_is_accepted():
    assert is_inn("500100732259")


def test_grouped_checksum_valid_inn_is_blocked_without_echoing_value():
    value = "5001 0073-2259"
    assert is_inn(value)
    findings = scan_text(f"safe-prefix {value} safe-suffix", forbidden_tokens=[])
    matching = [finding for finding in findings if finding.kind == "inn_unlabeled"]
    assert matching
    assert all(value not in finding.evidence for finding in matching)


def test_checksum_valid_unlabeled_ogrn_is_blocked():
    value = "1234567890127"
    assert is_ogrn(value)
    assert any(finding.kind == "ogrn_unlabeled" for finding in scan_text(value, forbidden_tokens=[]))


def test_grouped_checksum_valid_ogrn_is_blocked():
    value = "1234\u00a05678\u20099012-7"
    assert is_ogrn(value)
    assert any(finding.kind == "ogrn_unlabeled" for finding in scan_text(value, forbidden_tokens=[]))


def test_arbitrary_product_number_is_not_mislabeled_as_tax_identifier():
    value = "1234567890"
    assert not is_inn(value)
    assert not is_ogrn(value)
    assert not any(
        finding.kind in {"inn_unlabeled", "ogrn_unlabeled"}
        for finding in scan_text(f"Артикул {value}", forbidden_tokens=[])
    )
