from __future__ import annotations

from pathlib import Path
import zipfile

from stroy_snab.anonymization import scan_path, write_sanitized_workbook


def test_scan_path_freezes_generator_denylist_before_multi_part_scan(tmp_path: Path):
    path = tmp_path / "document.xlsx"
    write_sanitized_workbook(
        path,
        sheets=[{"name": "REQUEST", "rows": [["SECRET_TOKEN"]]}],
        forbidden_tokens=[],
    )

    report = scan_path(path, forbidden_tokens=(token for token in ["SECRET_TOKEN"]))

    assert any(finding.kind == "forbidden_token" for finding in report.findings)
    assert not report.passed


def test_xlsx_case_ambiguous_duplicate_member_is_blocked(tmp_path: Path):
    clean = tmp_path / "clean.xlsx"
    write_sanitized_workbook(
        clean,
        sheets=[{"name": "REQUEST", "rows": [["Кабель", 1]]}],
        forbidden_tokens=[],
    )
    poisoned = tmp_path / "poisoned.xlsx"

    with zipfile.ZipFile(clean, "r") as source, zipfile.ZipFile(poisoned, "w") as target:
        for item in source.infolist():
            target.writestr(item, source.read(item.filename))
        target.writestr("[CONTENT_TYPES].XML", source.read("[Content_Types].xml"))

    report = scan_path(poisoned, forbidden_tokens=[])

    assert any(finding.kind == "xlsx_duplicate_member" for finding in report.findings)
    assert not report.passed
