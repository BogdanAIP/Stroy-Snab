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


@pytest.mark.parametrize(
    "ambiguous_quantity",
    [
        "1.200,50",
        "12.03.2024",
        "3х2,5",
        "20/25",
        "10±1",
    ],
)
def test_rejects_ambiguous_quantity_syntax(
    tmp_path: Path,
    ambiguous_quantity: str,
) -> None:
    path = tmp_path / "ambiguous.xlsx"
    _save(
        path,
        [
            ["Наименование", "Кол-во"],
            ["Материал", ambiguous_quantity],
        ],
    )

    with pytest.raises(XlsxLineExtractionError, match="unparseable quantity"):
        extract_xlsx_lines(
            path,
            document_id="REQUEST_0004",
            document_role="REQUEST",
        )


def test_quantity_places_does_not_override_actual_quantity(tmp_path: Path) -> None:
    path = tmp_path / "delivery.xlsx"
    _save(
        path,
        [
            ["Наименование товара", "Ед. изм.", "Количество мест", "Кол-во"],
            ["Кабель ВВГ 3х2,5", "м", 3, 300],
        ],
    )

    lines = extract_xlsx_lines(
        path,
        document_id="DELIVERY_0001",
        document_role="UPD_OR_DELIVERY",
    )

    assert len(lines) == 1
    assert lines[0].quantity == Decimal("300")
    assert lines[0].unit_raw == "м"


def test_rejects_multiple_supported_quantity_headers(tmp_path: Path) -> None:
    path = tmp_path / "ambiguous_headers.xlsx"
    _save(
        path,
        [
            ["Наименование", "Количество", "Кол-во"],
            ["Кабель", 10, 20],
        ],
    )

    with pytest.raises(XlsxLineExtractionError, match="ambiguous procurement table header roles"):
        extract_xlsx_lines(
            path,
            document_id="REQUEST_0005",
            document_role="REQUEST",
        )


def test_blank_unit_column_does_not_erase_quantity_suffix(tmp_path: Path) -> None:
    path = tmp_path / "blank_unit.xlsx"
    _save(
        path,
        [
            ["Наименование", "Кол-во", "Ед. изм."],
            ["Гвозди 100 мм", "48 шт", " "],
        ],
    )

    lines = extract_xlsx_lines(
        path,
        document_id="REQUEST_0006",
        document_role="REQUEST",
    )

    assert lines[0].quantity == Decimal("48")
    assert lines[0].unit_raw == "шт"


def test_nonempty_unit_column_overrides_quantity_suffix(tmp_path: Path) -> None:
    path = tmp_path / "explicit_unit.xlsx"
    _save(
        path,
        [
            ["Наименование", "Кол-во", "Ед. изм."],
            ["Кабель", "48 шт", "м"],
        ],
    )

    lines = extract_xlsx_lines(
        path,
        document_id="REQUEST_0007",
        document_role="REQUEST",
    )

    assert lines[0].quantity == Decimal("48")
    assert lines[0].unit_raw == "м"


def test_formula_quantity_fails_closed_even_when_other_rows_are_valid(tmp_path: Path) -> None:
    path = tmp_path / "formula.xlsx"
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Заявка"
    worksheet.append(["Наименование", "Кол-во"])
    worksheet.append(["Кабель", 10])
    worksheet.append(["Провод", "=B2*2"])
    workbook.save(path)
    workbook.close()

    with pytest.raises(XlsxLineExtractionError, match="formula quantity is unsupported"):
        extract_xlsx_lines(
            path,
            document_id="REQUEST_0008",
            document_role="REQUEST",
        )


def test_missing_quantity_in_candidate_row_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "missing_quantity.xlsx"
    _save(
        path,
        [
            ["Наименование", "Кол-во"],
            ["Кабель", 10],
            ["Провод", None],
        ],
    )

    with pytest.raises(XlsxLineExtractionError, match="unparseable quantity"):
        extract_xlsx_lines(
            path,
            document_id="REQUEST_0009",
            document_role="REQUEST",
        )


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
        document_id="REQUEST_0010",
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
            document_id="REQUEST_0011",
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

    with pytest.raises(XlsxLineExtractionError, match="unparseable quantity"):
        extract_xlsx_lines(
            path,
            document_id="REQUEST_0012",
            document_role="REQUEST",
        )
