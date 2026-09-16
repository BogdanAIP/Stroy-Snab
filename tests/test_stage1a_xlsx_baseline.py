from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import openpyxl
import pytest

from stroy_snab.experiments.stage1a_xlsx import (
    XlsxLineExtractionError,
    extract_xlsx_lines,
)


def _save(path: Path, rows: list[list[object]]) -> None:
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Заявка"
    for row in rows:
        worksheet.append(row)
    workbook.save(path)
    workbook.close()


def test_extracts_canonical_lines_and_source_locator(tmp_path: Path) -> None:
    path = tmp_path / "request.xlsx"
    _save(
        path,
        [
            ["Заявка на материалы"],
            [None],
            ["№", "Наименование товара", "Ед. изм.", "Кол-во"],
            [1, "Кабель ВВГнг(А)-LS 3x2,5", "м", 50],
            [2, "Автоматический выключатель 16А", "шт", 6],
            [None, "Итого", None, 56],
        ],
    )

    lines = extract_xlsx_lines(
        path,
        document_id="REQUEST_0001",
        document_role="REQUEST",
    )

    assert len(lines) == 2
    assert lines[0].document_id == "REQUEST_0001"
    assert lines[0].document_role == "REQUEST"
    assert lines[0].item_name_raw == "Кабель ВВГнг(А)-LS 3x2,5"
    assert lines[0].unit_raw == "м"
    assert lines[0].quantity == Decimal("50")
    assert lines[0].source_locator == "Заявка!B4"


def test_accepts_header_variants_and_decimal_comma(tmp_path: Path) -> None:
    path = tmp_path / "request.xlsx"
    _save(
        path,
        [
            ["Наименование материала", "Единица измерения", "Количество (объем)"],
            ["Смесь сухая", "кг", "1 200,5"],
        ],
    )

    lines = extract_xlsx_lines(
        path,
        document_id="REQUEST_0002",
        document_role="REQUEST",
    )

    assert len(lines) == 1
    assert lines[0].quantity == Decimal("1200.5")
    assert lines[0].unit_raw == "кг"


def test_extracts_unit_from_combined_quantity_cell(tmp_path: Path) -> None:
    path = tmp_path / "request.xlsx"
    _save(
        path,
        [
            ["№ п/п", "Наименование", "Кол-во", "Комментарий"],
            [1, "Шпилька резьбовая М12х1000 ОЦ", "48 шт", None],
        ],
    )

    lines = extract_xlsx_lines(
        path,
        document_id="REQUEST_0003",
        document_role="REQUEST",
    )

    assert lines[0].quantity == Decimal("48")
    assert lines[0].unit_raw == "шт"
    assert lines[0].source_locator == "Заявка!B2"


def test_unit_column_is_optional_but_provenance_is_preserved(tmp_path: Path) -> None:
    path = tmp_path / "request.xlsx"
    _save(
        path,
        [
            ["Товар", "Количество"],
            ["Грунтовка", 3],
        ],
    )

    lines = extract_xlsx_lines(
        path,
        document_id="REQUEST_0003",
        document_role="REQUEST",
    )

    assert lines[0].unit_raw is None
    assert lines[0].source_locator == "Заявка!A2"


def test_fails_closed_when_no_supported_table_exists(tmp_path: Path) -> None:
    path = tmp_path / "notes.xlsx"
    _save(path, [["Комментарий", "Значение"], ["Примечание", 10]])

    with pytest.raises(XlsxLineExtractionError, match="no supported procurement table"):
        extract_xlsx_lines(
            path,
            document_id="REQUEST_0004",
            document_role="REQUEST",
        )


def test_fails_closed_when_header_exists_but_no_numeric_quantity(tmp_path: Path) -> None:
    path = tmp_path / "empty.xlsx"
    _save(
        path,
        [
            ["Наименование", "Ед. изм.", "Количество"],
            ["Кабель", "м", "не указано"],
        ],
    )

    with pytest.raises(XlsxLineExtractionError, match="no procurement lines"):
        extract_xlsx_lines(
            path,
            document_id="REQUEST_0005",
            document_role="REQUEST",
        )
