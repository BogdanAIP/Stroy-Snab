from __future__ import annotations

import json
from pathlib import Path

from stroy_snab.anonymization import scan_path, validate_public_manifest


ROOT = Path(__file__).resolve().parents[1]
FIXTURES_ROOT = ROOT / "data" / "fixtures" / "documents" / "anonymized-real"


def _manifests() -> list[Path]:
    manifests = sorted(FIXTURES_ROOT.glob("CASE_*/manifest.json"))
    assert manifests, "at least one anonymized-real manifest is required"
    return manifests


def test_anonymized_real_manifests_and_derivatives_are_self_consistent():
    for manifest_path in _manifests():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        validate_public_manifest(manifest)
        case_dir = manifest_path.parent
        assert case_dir.name == manifest["case_id"]

        for document in manifest["documents"]:
            for relative_name in document["derivative_files"]:
                derivative = case_dir / relative_name
                assert derivative.is_file(), f"missing derivative for {document['document_id']}"

                report = scan_path(derivative, forbidden_tokens=[])
                assert report.automated_checks_passed, [finding.kind for finding in report.findings]

                if derivative.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                    assert document["manual_visual_review"] is True
                    assert report.requires_manual_visual_review
                else:
                    assert report.passed


def test_anonymized_real_case_directories_contain_only_manifested_files():
    for manifest_path in _manifests():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        case_dir = manifest_path.parent
        declared = {
            manifest_path.resolve(),
            *{
                (case_dir / relative_name).resolve()
                for document in manifest["documents"]
                for relative_name in document["derivative_files"]
            },
        }
        actual = {path.resolve() for path in case_dir.rglob("*") if path.is_file()}
        assert actual == declared
