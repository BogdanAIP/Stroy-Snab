from __future__ import annotations

from pathlib import Path
import os
import tempfile
from typing import Any, Iterable

import xlsxwriter

from .leakcheck import scan_text


def _validate_sheet_name(name: str, forbidden_tokens: Iterable[str]) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("sheet name must be non-empty")
    if len(name) > 31 or any(char in name for char in "[]:*?/\\"):
        raise ValueError(f"invalid XLSX sheet name: {name!r}")
    findings = scan_text(name, location="sheet-name", forbidden_tokens=forbidden_tokens)
    if findings:
        raise ValueError("sheet name contains data blocked by leak policy")
    return name


def _validate_cell_value(value: Any, forbidden_tokens: Iterable[str]) -> Any:
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if not isinstance(value, str):
        raise TypeError(f"unsupported sanitized cell type: {type(value).__name__}")
    findings = scan_text(value, location="cell", forbidden_tokens=forbidden_tokens)
    if findings:
        raise ValueError("sanitized cell contains data blocked by leak policy")
    return value


def write_sanitized_workbook(
    output_path: str | Path,
    *,
    sheets: list[dict[str, Any]],
    forbidden_tokens: Iterable[str],
) -> Path:
    """Create a new XLSX from an explicitly sanitized allowlist representation.

    This function intentionally never opens or copies an original workbook.
    Callers must first map private input into allowed sheet names, values, widths
    and merge ranges. Formula and URL auto-detection are disabled so private or
    active content cannot be smuggled through a string value.
    """
    if not sheets:
        raise ValueError("at least one sanitized sheet is required")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp.xlsx", dir=output.parent)
    os.close(fd)
    temp_path = Path(temp_name)

    workbook = xlsxwriter.Workbook(
        temp_path,
        {
            "strings_to_formulas": False,
            "strings_to_urls": False,
            "strings_to_numbers": False,
        },
    )
    workbook.set_properties(
        {
            "title": "Stroy-Snab anonymized fixture",
            "subject": "anonymized-real evaluation derivative",
            "author": "Stroy-Snab",
            "manager": "",
            "company": "",
            "category": "evaluation fixture",
            "keywords": "",
            "comments": "No reverse mapping to private source is stored in this file.",
        }
    )

    try:
        for sheet_spec in sheets:
            unknown = set(sheet_spec) - {"name", "rows", "column_widths", "merges"}
            if unknown:
                raise ValueError(f"unknown sanitized sheet fields: {sorted(unknown)}")
            name = _validate_sheet_name(sheet_spec.get("name", ""), forbidden_tokens)
            rows = sheet_spec.get("rows")
            if not isinstance(rows, list):
                raise ValueError("rows must be a list")
            worksheet = workbook.add_worksheet(name)

            widths = sheet_spec.get("column_widths", {})
            if not isinstance(widths, dict):
                raise ValueError("column_widths must be an object")
            for col, width in widths.items():
                if not isinstance(col, int) or col < 0 or not isinstance(width, (int, float)):
                    raise ValueError("column_widths must map non-negative integer columns to numeric widths")
                worksheet.set_column(col, col, min(float(width), 80.0))

            for row_idx, row in enumerate(rows):
                if not isinstance(row, list):
                    raise ValueError("each row must be a list")
                for col_idx, raw_value in enumerate(row):
                    value = _validate_cell_value(raw_value, forbidden_tokens)
                    worksheet.write(row_idx, col_idx, value)

            merges = sheet_spec.get("merges", [])
            if not isinstance(merges, list):
                raise ValueError("merges must be a list")
            for merge in merges:
                if not (isinstance(merge, dict) and set(merge) == {"first_row", "first_col", "last_row", "last_col"}):
                    raise ValueError("merge must contain first_row/first_col/last_row/last_col")
                coords = [merge[k] for k in ("first_row", "first_col", "last_row", "last_col")]
                if not all(isinstance(v, int) and v >= 0 for v in coords):
                    raise ValueError("merge coordinates must be non-negative integers")
                worksheet.merge_range(*coords, "")
    except Exception:
        try:
            workbook.close()
        finally:
            temp_path.unlink(missing_ok=True)
        raise
    else:
        workbook.close()
        os.replace(temp_path, output)
    return output
