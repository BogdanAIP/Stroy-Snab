from __future__ import annotations

import json
from pathlib import Path
import zipfile

import openpyxl
import pytest

from stroy_snab.anonymization import (
    NeutralIdAllocator,
    build_public_manifest,
    scan_path,
    scan_text,
    validate_public_manifest,
    write_sanitized_workbook,
)


def test_neutral_ids_are_allocator_owned_and_fixed_width():
    allocator = NeutralIdAllocator()
    assert allocator.allocate("case") == "CASE_0001"
    assert allocator.allocate("case") == "CASE_0002"
    assert allocator.allocate("invoice") == "INVOICE_0001"
    with pytest.raises(ValueError):
        allocator.allocate("supplier")


def test_manifest_rejects_reverse_private_fields():
    manifest = build_public_manifest(
        case_id="CASE_0001",
        provenance="anonymized-real",
        documents=[
            {
                "document_id": "REQUEST_0001",
                "role": "REQUEST",
                "format": "xlsx",
                "derivative_files": ["REQUEST_0001/document.xlsx"],
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
    assert any(f.kind == "xlsx_unapproved_part" for f in report.findings)
    assert not report.passed


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
                "derivative_files": ["DOC_0001/expected.json"],
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
            case_id="CASE_0001",
            provenance="anonymized-real",
            documents=[
                {
                    "document_id": "REQUEST_0001",
                    "role": "REQUEST",
                    "format": "xlsx",
                    "derivative_files": ["REQUEST_0001/supplier-real-name.xlsx"],
                    "manual_visual_review": True,
                }
            ],
        )


def test_manifest_rejects_wrong_document_root_or_format_mismatch():
    with pytest.raises(ValueError):
        build_public_manifest(
            case_id="CASE_0004",
            provenance="synthetic",
            documents=[
                {
                    "document_id": "REQUEST_0001",
                    "role": "REQUEST",
                    "format": "xlsx",
                    "derivative_files": ["INVOICE_0001/document.xlsx"],
                    "manual_visual_review": False,
                }
            ],
        )

    with pytest.raises(ValueError):
        build_public_manifest(
            case_id="CASE_0005",
            provenance="synthetic",
            documents=[
                {
                    "document_id": "REQUEST_0001",
                    "role": "REQUEST",
                    "format": "xlsx",
                    "derivative_files": ["REQUEST_0001/visual/page-001.png"],
                    "manual_visual_review": False,
                }
            ],
        )


def test_manifest_rejects_duplicate_document_ids():
    document = {
        "document_id": "REQUEST_0001",
        "role": "REQUEST",
        "format": "xlsx",
        "derivative_files": ["REQUEST_0001/document.xlsx"],
        "manual_visual_review": False,
    }
    with pytest.raises(ValueError):
        build_public_manifest(
            case_id="CASE_0006",
            provenance="synthetic",
            documents=[document, dict(document)],
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
    allocator = NeutralIdAllocator()
    with pytest.raises(ValueError) as exc:
        allocator.allocate("Secret Supplier LLC")
    assert "Secret Supplier LLC" not in str(exc.value)


def test_real_manifest_rejects_date_like_case_id_and_source_number_document_id():
    with pytest.raises(ValueError):
        build_public_manifest(
            case_id="CASE_2026",
            provenance="anonymized-real",
            documents=[
                {
                    "document_id": "REQUEST_0001",
                    "role": "REQUEST",
                    "format": "xlsx",
                    "derivative_files": ["REQUEST_0001/document.xlsx"],
                    "manual_visual_review": False,
                }
            ],
        )

    with pytest.raises(ValueError):
        build_public_manifest(
            case_id="CASE_20260910",
            provenance="anonymized-real",
            documents=[
                {
                    "document_id": "REQUEST_0001",
                    "role": "REQUEST",
                    "format": "xlsx",
                    "derivative_files": ["REQUEST_0001/document.xlsx"],
                    "manual_visual_review": False,
                }
            ],
        )

    with pytest.raises(ValueError):
        build_public_manifest(
            case_id="CASE_0001",
            provenance="anonymized-real",
            documents=[
                {
                    "document_id": "INVOICE_5606",
                    "role": "OFFER_OR_INVOICE",
                    "format": "xlsx",
                    "derivative_files": ["INVOICE_5606/document.xlsx"],
                    "manual_visual_review": False,
                }
            ],
        )


def test_manifest_requires_dense_document_allocation_per_prefix():
    manifest = build_public_manifest(
        case_id="CASE_0001",
        provenance="synthetic",
        documents=[
            {
                "document_id": "REQUEST_0001",
                "role": "REQUEST",
                "format": "xlsx",
                "derivative_files": ["REQUEST_0001/document.xlsx"],
                "manual_visual_review": False,
            },
            {
                "document_id": "REQUEST_0002",
                "role": "REQUEST",
                "format": "xlsx",
                "derivative_files": ["REQUEST_0002/document.xlsx"],
                "manual_visual_review": False,
            },
        ],
    )
    assert [d["document_id"] for d in manifest["documents"]] == ["REQUEST_0001", "REQUEST_0002"]

    with pytest.raises(ValueError):
        build_public_manifest(
            case_id="CASE_0001",
            provenance="synthetic",
            documents=[
                {
                    "document_id": "REQUEST_0002",
                    "role": "REQUEST",
                    "format": "xlsx",
                    "derivative_files": ["REQUEST_0002/document.xlsx"],
                    "manual_visual_review": False,
                }
            ],
        )
