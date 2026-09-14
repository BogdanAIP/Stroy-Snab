from __future__ import annotations

from copy import deepcopy
from pathlib import PurePosixPath
from typing import Any

from .ids import _neutral_id_parts, _validate_neutral_id

_ALLOWED_TOP_LEVEL = {"schema_version", "case_id", "provenance", "documents"}
_ALLOWED_DOCUMENT_KEYS = {
    "document_id",
    "role",
    "format",
    "derivative_files",
    "manual_visual_review",
}
_ALLOWED_ROLES = {
    "REQUEST",
    "SPECIFICATION",
    "OFFER_OR_INVOICE",
    "UPD_OR_DELIVERY",
    "INCOMING_CONTROL",
    "OTHER",
}
_ALLOWED_PROVENANCE = {"anonymized-real", "synthetic", "minimal-redacted", "public-source"}
_REAL_DERIVED_PROVENANCE = {"anonymized-real", "minimal-redacted"}
_FORBIDDEN_KEY_FRAGMENTS = {
    "source_path",
    "source_filename",
    "original_filename",
    "original_id",
    "real_id",
    "supplier_name",
    "buyer_name",
    "contractor_name",
    "inn",
    "kpp",
    "ogrn",
    "address",
    "email",
    "phone",
}


def _walk_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            folded = str(key).casefold()
            if any(fragment in folded for fragment in _FORBIDDEN_KEY_FRAGMENTS):
                raise ValueError("forbidden reverse/private field in public manifest")
            _walk_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_keys(nested)


def _validate_derivative_path(value: str, *, document_id: str, document_format: str) -> None:
    if "\\" in value or value.startswith("/") or ".." in PurePosixPath(value).parts:
        raise ValueError("derivative_files must contain safe relative POSIX paths only")
    path = PurePosixPath(value)
    if not path.parts or path.parts[0] != document_id:
        raise ValueError("derivative path must be rooted under its document_id")

    if document_format == "xlsx":
        expected = PurePosixPath(document_id, "document.xlsx")
        if path != expected:
            raise ValueError("xlsx derivative path does not match manifest format")
        return

    if document_format == "json":
        expected = PurePosixPath(document_id, "expected.json")
        if path != expected:
            raise ValueError("json derivative path does not match manifest format")
        return

    if document_format == "png":
        if len(path.parts) != 3 or path.parts[1] != "visual":
            raise ValueError("png derivative must live under document_id/visual")
        filename = path.name
        if not (filename.startswith("page-") and filename.endswith(".png") and filename[5:-4].isdigit()):
            raise ValueError("png derivative must use neutral page-NNN.png naming")
        return

    raise ValueError("unsupported public derivative format")


def validate_public_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    _walk_keys(manifest)
    unknown_top = set(manifest) - _ALLOWED_TOP_LEVEL
    if unknown_top:
        raise ValueError("unknown public manifest fields present")
    if manifest.get("schema_version") != "1.0":
        raise ValueError("schema_version must be '1.0'")

    case_id = _validate_neutral_id(manifest.get("case_id", ""))
    case_prefix, case_ordinal = _neutral_id_parts(case_id)
    if case_prefix != "CASE":
        raise ValueError("case_id must use CASE prefix")

    provenance = manifest.get("provenance")
    if provenance not in _ALLOWED_PROVENANCE:
        raise ValueError("unsupported provenance")
    # Stage 1P v1 intentionally keeps the real-derived public surface to one
    # independently allocated case. Expanding real-derived case numbering
    # requires a separately reviewed repository-level allocation mechanism.
    if provenance in _REAL_DERIVED_PROVENANCE and case_ordinal != 1:
        raise ValueError("Stage 1P real-derived public case_id must be CASE_0001")

    documents = manifest.get("documents")
    if not isinstance(documents, list) or not documents:
        raise ValueError("documents must be a non-empty list")

    seen_document_ids: set[str] = set()
    seen_derivative_paths: set[str] = set()
    next_ordinal_by_prefix: dict[str, int] = {}

    for doc in documents:
        if not isinstance(doc, dict):
            raise ValueError("each document must be an object")
        unknown = set(doc) - _ALLOWED_DOCUMENT_KEYS
        if unknown:
            raise ValueError("unknown public document fields present")

        document_id = _validate_neutral_id(doc.get("document_id", ""))
        if document_id in seen_document_ids:
            raise ValueError("duplicate document_id in public manifest")
        seen_document_ids.add(document_id)

        prefix, ordinal = _neutral_id_parts(document_id)
        if prefix == "CASE":
            raise ValueError("document_id must not use CASE prefix")
        expected_ordinal = next_ordinal_by_prefix.get(prefix, 0) + 1
        if ordinal != expected_ordinal:
            raise ValueError("document_id must follow dense public allocation order")
        next_ordinal_by_prefix[prefix] = ordinal

        if doc.get("role") not in _ALLOWED_ROLES:
            raise ValueError("unsupported document role")
        document_format = doc.get("format")
        if document_format not in {"xlsx", "png", "json"}:
            raise ValueError("public derivative format must be xlsx/png/json in Stage 1P prototype")

        files = doc.get("derivative_files")
        if not isinstance(files, list) or not files or not all(isinstance(x, str) for x in files):
            raise ValueError("derivative_files must be a non-empty list of relative paths")
        if document_format in {"xlsx", "json"} and len(files) != 1:
            raise ValueError("xlsx/json document must have exactly one derivative file")
        for item in files:
            _validate_derivative_path(item, document_id=document_id, document_format=document_format)
            if item in seen_derivative_paths:
                raise ValueError("duplicate derivative path in public manifest")
            seen_derivative_paths.add(item)

        manual_visual_review = doc.get("manual_visual_review")
        if not isinstance(manual_visual_review, bool):
            raise ValueError("manual_visual_review must be boolean")
        has_visual_derivative = document_format == "png"
        if provenance in _REAL_DERIVED_PROVENANCE and has_visual_derivative and not manual_visual_review:
            raise ValueError("real-derived visual fixtures require completed manual visual review")
    return manifest


def build_public_manifest(*, case_id: str, provenance: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
    manifest = {
        "schema_version": "1.0",
        "case_id": case_id,
        "provenance": provenance,
        "documents": deepcopy(documents),
    }
    return validate_public_manifest(manifest)
