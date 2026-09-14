from __future__ import annotations

from pathlib import Path
import warnings
import zipfile

import stroy_snab.anonymization.leakcheck as leakcheck
from stroy_snab.anonymization import scan_path, write_sanitized_workbook


def _clean_workbook(path: Path) -> None:
    write_sanitized_workbook(
        path,
        sheets=[{"name": "REQUEST", "rows": [["Наименование", "Количество"], ["Кабель", 10]]}],
        forbidden_tokens=[],
    )


def _copy_zip_with_extra(source: Path, target: Path, name: str, payload: bytes) -> None:
    with zipfile.ZipFile(source, "r") as src, zipfile.ZipFile(target, "w") as dst:
        for item in src.infolist():
            dst.writestr(item, src.read(item.filename))
        dst.writestr(name, payload)


def test_public_xlsx_rejects_unapproved_media_part(tmp_path: Path):
    clean = tmp_path / "clean.xlsx"
    poisoned = tmp_path / "poisoned.xlsx"
    _clean_workbook(clean)
    _copy_zip_with_extra(clean, poisoned, "xl/media/image1.png", b"private-image-bytes")

    report = scan_path(poisoned, forbidden_tokens=[])
    assert any(f.kind == "xlsx_unapproved_part" for f in report.findings)
    assert not report.passed


def test_public_xlsx_rejects_duplicate_member_names(tmp_path: Path):
    clean = tmp_path / "clean.xlsx"
    poisoned = tmp_path / "poisoned.xlsx"
    _clean_workbook(clean)

    with zipfile.ZipFile(clean, "r") as src, zipfile.ZipFile(poisoned, "w") as dst:
        for item in src.infolist():
            dst.writestr(item, src.read(item.filename))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            dst.writestr("xl/workbook.xml", b"<workbook/>")

    report = scan_path(poisoned, forbidden_tokens=[])
    assert any(f.kind == "xlsx_duplicate_member" for f in report.findings)
    assert not report.passed


def test_public_xlsx_rejects_unsafe_member_path(tmp_path: Path):
    clean = tmp_path / "clean.xlsx"
    poisoned = tmp_path / "poisoned.xlsx"
    _clean_workbook(clean)
    _copy_zip_with_extra(clean, poisoned, "../private.txt", b"secret")

    report = scan_path(poisoned, forbidden_tokens=[])
    assert any(f.kind in {"xlsx_unsafe_member_path", "xlsx_unapproved_part"} for f in report.findings)
    assert not report.passed


def test_public_xlsx_enforces_member_size_limit(tmp_path: Path, monkeypatch):
    clean = tmp_path / "clean.xlsx"
    _clean_workbook(clean)
    monkeypatch.setattr(leakcheck, "_MAX_XLSX_MEMBER_BYTES", 64)

    report = scan_path(clean, forbidden_tokens=[])
    assert any(f.kind == "xlsx_resource_limit" for f in report.findings)
    assert not report.passed
