from __future__ import annotations

from pathlib import Path

import pytest

from stroy_snab.anonymization import scan_path, write_sanitized_workbook


def test_xlsx_writer_materializes_one_shot_denylist(tmp_path: Path):
    output = tmp_path / "document.xlsx"
    tokens = iter(["Secret Supplier"])

    with pytest.raises(ValueError):
        write_sanitized_workbook(
            output,
            sheets=[{"name": "REQUEST", "rows": [["safe"], ["Secret Supplier"]]}],
            forbidden_tokens=tokens,
        )

    assert not output.exists()


def test_scan_path_materializes_one_shot_denylist(tmp_path: Path):
    output = tmp_path / "document.xlsx"
    write_sanitized_workbook(
        output,
        sheets=[{"name": "REQUEST", "rows": [["safe"], ["Secret Supplier"]]}],
        forbidden_tokens=[],
    )

    report = scan_path(output, forbidden_tokens=iter(["Secret Supplier"]))
    assert any(finding.kind == "forbidden_token" for finding in report.findings)
    assert not report.passed


def test_non_string_denylist_entries_are_rejected(tmp_path: Path):
    output = tmp_path / "document.xlsx"
    with pytest.raises(TypeError):
        write_sanitized_workbook(
            output,
            sheets=[{"name": "REQUEST", "rows": [["safe"]]}],
            forbidden_tokens=[123],
        )

    with pytest.raises(TypeError):
        scan_path(output, forbidden_tokens=[123])
