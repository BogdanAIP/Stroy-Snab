from __future__ import annotations

from pathlib import Path

import openpyxl
import pytest

from stroy_snab.anonymization import write_sanitized_workbook


def test_xlsx_rebuild_rejects_writer_truncation(tmp_path: Path):
    output = tmp_path / "document.xlsx"
    too_long = "x" * 32768

    with pytest.raises(ValueError):
        write_sanitized_workbook(
            output,
            sheets=[{"name": "REQUEST", "rows": [[too_long]]}],
            forbidden_tokens=[],
        )

    assert not output.exists()


def test_xlsx_merge_preserves_top_left_value(tmp_path: Path):
    output = tmp_path / "document.xlsx"
    write_sanitized_workbook(
        output,
        sheets=[
            {
                "name": "REQUEST",
                "rows": [["Заголовок", None], ["Кабель", 10]],
                "merges": [{"first_row": 0, "first_col": 0, "last_row": 0, "last_col": 1}],
            }
        ],
        forbidden_tokens=[],
    )

    workbook = openpyxl.load_workbook(output, data_only=False, read_only=False)
    worksheet = workbook["REQUEST"]
    assert worksheet["A1"].value == "Заголовок"
    assert "A1:B1" in {str(item) for item in worksheet.merged_cells.ranges}


def test_xlsx_merge_rejects_discarding_non_empty_cell(tmp_path: Path):
    output = tmp_path / "document.xlsx"

    with pytest.raises(ValueError):
        write_sanitized_workbook(
            output,
            sheets=[
                {
                    "name": "REQUEST",
                    "rows": [["left", "must-not-disappear"]],
                    "merges": [{"first_row": 0, "first_col": 0, "last_row": 0, "last_col": 1}],
                }
            ],
            forbidden_tokens=[],
        )

    assert not output.exists()


def test_xlsx_rebuild_does_not_replace_existing_output(tmp_path: Path):
    output = tmp_path / "document.xlsx"
    output.write_bytes(b"existing-evidence")

    with pytest.raises(FileExistsError):
        write_sanitized_workbook(
            output,
            sheets=[{"name": "REQUEST", "rows": [["safe"]]}],
            forbidden_tokens=[],
        )

    assert output.read_bytes() == b"existing-evidence"
