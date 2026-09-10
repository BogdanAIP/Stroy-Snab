from __future__ import annotations

import json
from pathlib import Path
import zipfile

import openpyxl
import pytest

from stroy_snab.anonymization import (
    build_public_manifest,
    neutral_id,
    scan_path,
    scan_text,
    validate_public_manifest,
    write_sanitized_workbook,
)


def test_neutral_ids_use_only_prefix_and_ordinal():
    assert neutral_id("case", 1) == "CASE_0001"
    assert neutral_id("invoice", 27) == "INVOICE_0027"
    with pytest.raises(ValueError):
        neutral_id("supplier", 1)


def test_manifest_rejects_reverse_private_fields():
    manifest = build_public_manifest(
        case_id="CASE_0001",
        provenance="anonymized-real",
        documents=[
            {
                "document_id": "REQUEST_0001",
                "role": "REQUEST",
                "format": "xlsx",
                "derivative_files": ["document.xlsx"],
                "manual_visual_review": True,
            }
        ],
    )
    assert validate_public_manifest(manifest) is manifest
    bad = dict(manifest)
    bad["source_filename"] = "private.xlsx"
    with pytest.raises(ValueError):
        validate_public_manifest(bad)


def test_scan_text_detects_generic_identifiers_without_echoing_local_denylist():
    findings = scan_text(
        "ИНН 7701234567, mail person@example.org, https://supplier.example/item",
        forbidden_tokens=["Secret Supplier LLC"],
    )
    kinds = {f.kind for f in findings}
    assert {"inn", "email", "url"}.issubset(kinds)
    rendered = " ".join(f.evidence for f in findings)
    assert "7701234567" not in rendered
    assert "person@example.org" not in rendered

    deny = scan_text("Order for Secret Supplier LLC", forbidden_tokens=["Secret Supplier LLC"])
    assert deny[0].kind == "forbidden_token"
    assert deny[0].evidence == "matched local denylist token"
    assert "Secret Supplier LLC" not in str(deny[0])


def test_rebuilt_xlsx_rejects_url_like_content(tmp_path: Path):
    output = tmp_path / "REQUEST_0001.xlsx"
    with pytest.raises(ValueError):
        write_sanitized_workbook(
            output,
            sheets=[
                {
                    "name": "REQUEST",
                    "rows": [["www.example.invalid/not-a-link", 3]],
                }
            ],
            forbidden_tokens=[],
        )


def test_rebuilt_xlsx_is_clean_and_formula_string_is_inert(tmp_path: Path):
    output = tmp_path / "REQUEST_0002.xlsx"
    write_sanitized_workbook(
        output,
        sheets=[
            {
                "name": "REQUEST",
                "rows": [["Наименование", "Количество"], ["=1+1", 2]],
                "column_widths": {0: 30},
                "merges": [],
            }
        ],
        forbidden_tokens=[],
    )
    report = scan_path(output, forbidden_tokens=[])
    assert report.passed, report.findings
    with zipfile.ZipFile(output) as archive:
        names = {n.lower() for n in archive.namelist()}
        assert not any("externallinks" in n for n in names)
        assert not any("comments" in n for n in names)
        assert not any("vba" in n for n in names)
        sheet_xml = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")
        assert "<f>" not in sheet_xml
    workbook = openpyxl.load_workbook(output, data_only=False, read_only=True)
    assert workbook["REQUEST"]["A2"].value == "=1+1"
    assert workbook["REQUEST"]["A2"].data_type == "s"


def test_writer_rejects_blocking_content_before_file_is_publishable(tmp_path: Path):
    output = tmp_path / "REQUEST_0003.xlsx"
    with pytest.raises(ValueError):
        write_sanitized_workbook(
            output,
            sheets=[{"name": "REQUEST", "rows": [["contact@example.org"]]}],
            forbidden_tokens=[],
        )


def test_xlsx_leakcheck_detects_hidden_container_part(tmp_path: Path):
    clean = tmp_path / "clean.xlsx"
    write_sanitized_workbook(clean, sheets=[{"name": "REQUEST", "rows": [["Кабель", 10]]}], forbidden_tokens=[])
    poisoned = tmp_path / "poisoned.xlsx"
    with zipfile.ZipFile(clean, "r") as src, zipfile.ZipFile(poisoned, "w") as dst:
        for item in src.infolist():
            dst.writestr(item, src.read(item.filename))
        dst.writestr("xl/externalLinks/externalLink1.xml", "<secret>hidden</secret>")
    report = scan_path(poisoned, forbidden_tokens=[])
    assert any(f.kind == "forbidden_xlsx_part" for f in report.findings)


def test_json_leakcheck_and_manifest_file(tmp_path: Path):
    path = tmp_path / "manifest.json"
    manifest = build_public_manifest(
        case_id="CASE_0002",
        provenance="synthetic",
        documents=[
            {
                "document_id": "DOC_0001",
                "role": "OTHER",
                "format": "json",
                "derivative_files": ["expected.json"],
                "manual_visual_review": False,
            }
        ],
    )
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    assert scan_path(path, forbidden_tokens=[]).passed


def test_failed_rebuild_leaves_no_candidate_file(tmp_path: Path):
    output = tmp_path / "REQUEST_0004.xlsx"
    with pytest.raises(ValueError):
        write_sanitized_workbook(
            output,
            sheets=[{"name": "REQUEST", "rows": [["safe"], ["ИНН 7701234567"]]}],
            forbidden_tokens=[],
        )
    assert not output.exists()


def test_manifest_rejects_non_neutral_derivative_filename():
    with pytest.raises(ValueError):
        build_public_manifest(
            case_id="CASE_0003",
            provenance="anonymized-real",
            documents=[
                {
                    "document_id": "REQUEST_0003",
                    "role": "REQUEST",
                    "format": "xlsx",
                    "derivative_files": ["supplier-real-name.xlsx"],
                    "manual_visual_review": True,
                }
            ],
        )


def test_clean_png_requires_manual_visual_review(tmp_path: Path):
    from PIL import Image

    output = tmp_path / "page-001.png"
    Image.new("RGB", (20, 20), "white").save(output)
    report = scan_path(output, forbidden_tokens=[])
    assert report.automated_checks_passed
    assert report.requires_manual_visual_review
    assert not report.passed


def test_errors_do_not_echo_private_identifier():
    with pytest.raises(ValueError) as exc:
        neutral_id("Secret Supplier LLC", 1)
    assert "Secret Supplier LLC" not in str(exc.value)
