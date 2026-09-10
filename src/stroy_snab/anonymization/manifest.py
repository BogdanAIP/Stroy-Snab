from __future__ import annotations

from copy import deepcopy
from pathlib import PurePosixPath
from typing import Any

from .ids import validate_neutral_id

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


def _validate_derivative_path(value: str) -> None:
    if "\\" in value or value.startswith("/") or ".." in PurePosixPath(value).parts:
        raise ValueError("derivative_files must contain safe relative POSIX paths only")
    path = PurePosixPath(value)
    if len(path.parts) > 3:
        raise ValueError("derivative path is too deep for Stage 1P public fixtures")
    for directory in path.parts[:-1]:
        if directory == "visual":
            continue
        validate_neutral_id(directory)
    filename = path.name
    allowed = (
        filename in {"document.xlsx", "expected.json", "manifest.json"}
        or (filename.startswith("page-") and filename.endswith(".png") and filename[5:-4].isdigit())
    )
    if not allowed:
        raise ValueError("non-neutral derivative filename")


def validate_public_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    _walk_keys(manifest)
    unknown_top = set(manifest) - _ALLOWED_TOP_LEVEL
    if unknown_top:
        raise ValueError("unknown public manifest fields present")
    if manifest.get("schema_version") != "1.0":
        raise ValueError("schema_version must be '1.0'")
    validate_neutral_id(manifest.get("case_id", ""))
    if manifest.get("provenance") not in _ALLOWED_PROVENANCE:
        raise ValueError("unsupported provenance")

    documents = manifest.get("documents")
    if not isinstance(documents, list) or not documents:
        raise ValueError("documents must be a non-empty list")
    for doc in documents:
        if not isinstance(doc, dict):
            raise ValueError("each document must be an object")
        unknown = set(doc) - _ALLOWED_DOCUMENT_KEYS
        if unknown:
            raise ValueError("unknown public document fields present")
        validate_neutral_id(doc.get("document_id", ""))
        if doc.get("role") not in _ALLOWED_ROLES:
            raise ValueError("unsupported document role")
        if doc.get("format") not in {"xlsx", "png", "json"}:
            raise ValueError("public derivative format must be xlsx/png/json in Stage 1P prototype")
        files = doc.get("derivative_files")
        if not isinstance(files, list) or not files or not all(isinstance(x, str) for x in files):
            raise ValueError("derivative_files must be a non-empty list of relative paths")
        for item in files:
            _validate_derivative_path(item)
        if not isinstance(doc.get("manual_visual_review"), bool):
            raise ValueError("manual_visual_review must be boolean")
    return manifest


def build_public_manifest(*, case_id: str, provenance: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
    manifest = {
        "schema_version": "1.0",
        "case_id": case_id,
        "provenance": provenance,
        "documents": deepcopy(documents),
    }
    return validate_public_manifest(manifest)
