from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys

import pytest

from stroy_snab.evaluation.stage1a import GoldDocument, evaluate_stage1a
from stroy_snab.experiments.stage1a_xlsx import ProcurementLine


def _line(
    *,
    locator: str,
    item: str = "Кабель",
    unit: str | None = "м",
    quantity: str = "10",
    document_id: str = "REQUEST_0001",
    role: str = "REQUEST",
) -> ProcurementLine:
    return ProcurementLine(
        document_id=document_id,
        document_role=role,
        item_name_raw=item,
        unit_raw=unit,
        quantity=Decimal(quantity),
        source_locator=locator,
    )


def _gold(*lines: ProcurementLine) -> tuple[GoldDocument, ...]:
    return (
        GoldDocument(
            document_id="REQUEST_0001",
            document_role="REQUEST",
            path="fixture.xlsx",
            lines=tuple(lines),
        ),
    )


def test_perfect_evaluation_reports_full_accuracy() -> None:
    expected = _line(locator="Лист1!A2")
    evaluation = evaluate_stage1a(_gold(expected), [expected])

    metrics = evaluation.as_metrics()
    assert metrics["line_detection_precision"] == 1.0
    assert metrics["line_detection_recall"] == 1.0
    assert metrics["item_exact_accuracy"] == 1.0
    assert metrics["item_normalized_accuracy"] == 1.0
    assert metrics["unit_exact_accuracy"] == 1.0
    assert metrics["quantity_exact_accuracy"] == 1.0
    assert metrics["strict_line_accuracy"] == 1.0
    assert metrics["document_perfect_rate"] == 1.0


def test_missing_line_reduces_recall_and_field_accuracy() -> None:
    first = _line(locator="Лист1!A2")
    second = _line(locator="Лист1!A3", item="Провод", quantity="20")

    metrics = evaluate_stage1a(_gold(first, second), [first]).as_metrics()

    assert metrics["line_detection_precision"] == 1.0
    assert metrics["line_detection_recall"] == 0.5
    assert metrics["item_exact_accuracy"] == 0.5
    assert metrics["quantity_exact_accuracy"] == 0.5
    assert metrics["document_perfect_rate"] == 0.0


def test_extra_line_reduces_precision_and_document_perfect_rate() -> None:
    expected = _line(locator="Лист1!A2")
    extra = _line(locator="Лист1!A3", item="Провод")

    metrics = evaluate_stage1a(_gold(expected), [expected, extra]).as_metrics()

    assert metrics["line_detection_precision"] == 0.5
    assert metrics["line_detection_recall"] == 1.0
    assert metrics["document_perfect_rate"] == 0.0


def test_normalized_accuracy_is_separate_from_exact_accuracy() -> None:
    expected = _line(locator="Лист1!A2", item="Кабель Ёлка", unit="ШТ")
    actual = _line(locator="Лист1!A2", item="  кабель   елка  ", unit="шт")

    metrics = evaluate_stage1a(_gold(expected), [actual]).as_metrics()

    assert metrics["item_exact_accuracy"] == 0.0
    assert metrics["item_normalized_accuracy"] == 1.0
    assert metrics["unit_exact_accuracy"] == 0.0
    assert metrics["unit_normalized_accuracy"] == 1.0
    assert metrics["strict_line_accuracy"] == 0.0


def test_duplicate_prediction_keys_fail_closed() -> None:
    expected = _line(locator="Лист1!A2")

    with pytest.raises(ValueError, match="duplicate predicted line key"):
        evaluate_stage1a(_gold(expected), [expected, expected])


def test_public_runner_outputs_only_aggregate_metrics() -> None:
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [sys.executable, "scripts/evaluate_stage1a.py"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["experiment"] == "stage1a_xlsx_evaluation"
    assert payload["dataset"] == "public_anonymized_real"
    assert payload["documents_total"] == 1
    assert payload["documents_perfect"] == 1
    assert payload["gold_lines"] == 1
    assert payload["predicted_lines"] == 1
    assert payload["content_logged"] is False
    assert payload["paths_logged"] is False
    assert "Шпилька" not in completed.stdout
    assert "REQUEST!B3" not in completed.stdout
    assert "document.xlsx" not in completed.stdout



def test_runner_redacts_private_paths_on_failure(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    private_name = "PRIVATE_SUPPLIER_SECRET.xlsx"
    missing_gold = tmp_path / private_name

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/evaluate_stage1a.py",
            "--gold",
            str(missing_gold),
            "--dataset-label",
            "PRIVATE_CONTROL_A",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    combined = completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["evaluation_status"] == "ERROR"
    assert payload["content_logged"] is False
    assert payload["paths_logged"] is False
    assert private_name not in combined
    assert str(missing_gold) not in combined


def test_runner_rejects_unsafe_dataset_label_without_echoing_it() -> None:
    root = Path(__file__).resolve().parents[1]
    unsafe_label = "PRIVATE SUPPLIER / SECRET"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/evaluate_stage1a.py",
            "--dataset-label",
            unsafe_label,
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    combined = completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["dataset"] == "INVALID_DATASET_LABEL"
    assert unsafe_label not in combined
