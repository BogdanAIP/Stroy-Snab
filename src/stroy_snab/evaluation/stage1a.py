from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
import json
import re
from typing import Iterable, Sequence

from stroy_snab.experiments.stage1a_xlsx import ProcurementLine


@dataclass(frozen=True, slots=True)
class GoldDocument:
    document_id: str
    document_role: str
    path: str
    lines: tuple[ProcurementLine, ...]


@dataclass(frozen=True, slots=True)
class Stage1AEvaluation:
    documents_total: int
    documents_perfect: int
    extraction_failures: int
    gold_lines: int
    predicted_lines: int
    matched_locators: int
    item_exact_correct: int
    item_normalized_correct: int
    unit_exact_correct: int
    unit_normalized_correct: int
    quantity_exact_correct: int
    role_exact_correct: int
    strict_line_correct: int

    @staticmethod
    def _ratio(numerator: int, denominator: int) -> float:
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def as_metrics(self) -> dict[str, int | float]:
        return {
            "documents_total": self.documents_total,
            "documents_perfect": self.documents_perfect,
            "document_perfect_rate": self._ratio(
                self.documents_perfect,
                self.documents_total,
            ),
            "extraction_failures": self.extraction_failures,
            "gold_lines": self.gold_lines,
            "predicted_lines": self.predicted_lines,
            "matched_locators": self.matched_locators,
            "line_detection_precision": self._ratio(
                self.matched_locators,
                self.predicted_lines,
            ),
            "line_detection_recall": self._ratio(
                self.matched_locators,
                self.gold_lines,
            ),
            "item_exact_accuracy": self._ratio(
                self.item_exact_correct,
                self.gold_lines,
            ),
            "item_normalized_accuracy": self._ratio(
                self.item_normalized_correct,
                self.gold_lines,
            ),
            "unit_exact_accuracy": self._ratio(
                self.unit_exact_correct,
                self.gold_lines,
            ),
            "unit_normalized_accuracy": self._ratio(
                self.unit_normalized_correct,
                self.gold_lines,
            ),
            "quantity_exact_accuracy": self._ratio(
                self.quantity_exact_correct,
                self.gold_lines,
            ),
            "role_exact_accuracy": self._ratio(
                self.role_exact_correct,
                self.gold_lines,
            ),
            "strict_line_accuracy": self._ratio(
                self.strict_line_correct,
                self.gold_lines,
            ),
        }


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    text = value.replace("\u00a0", " ").strip().lower().replace("ё", "е")
    return re.sub(r"\s+", " ", text)


def load_gold_documents(path: str | Path) -> tuple[GoldDocument, ...]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise ValueError("unsupported Stage 1A gold schema_version")

    documents: list[GoldDocument] = []
    for document in payload.get("documents", []):
        document_id = str(document["document_id"])
        document_role = str(document["document_role"])
        lines = tuple(
            ProcurementLine(
                document_id=document_id,
                document_role=document_role,
                item_name_raw=str(line["item_name_raw"]),
                unit_raw=(
                    None
                    if line.get("unit_raw") is None
                    else str(line["unit_raw"])
                ),
                quantity=Decimal(str(line["quantity"])),
                source_locator=str(line["source_locator"]),
            )
            for line in document.get("lines", [])
        )
        if not lines:
            raise ValueError("gold document must contain at least one line")
        documents.append(
            GoldDocument(
                document_id=document_id,
                document_role=document_role,
                path=str(document["path"]),
                lines=lines,
            )
        )

    if not documents:
        raise ValueError("gold dataset must contain at least one document")
    return tuple(documents)


def _line_key(line: ProcurementLine) -> tuple[str, str]:
    return line.document_id, line.source_locator


def _index_unique(
    lines: Iterable[ProcurementLine],
    *,
    label: str,
) -> dict[tuple[str, str], ProcurementLine]:
    indexed: dict[tuple[str, str], ProcurementLine] = {}
    for line in lines:
        key = _line_key(line)
        if key in indexed:
            raise ValueError(f"duplicate {label} line key")
        indexed[key] = line
    return indexed


def evaluate_stage1a(
    gold_documents: Sequence[GoldDocument],
    predictions: Sequence[ProcurementLine],
    *,
    extraction_failures: int = 0,
) -> Stage1AEvaluation:
    gold_lines = tuple(
        line
        for document in gold_documents
        for line in document.lines
    )
    gold = _index_unique(gold_lines, label="gold")
    predicted = _index_unique(predictions, label="predicted")

    matched_keys = gold.keys() & predicted.keys()

    item_exact_correct = 0
    item_normalized_correct = 0
    unit_exact_correct = 0
    unit_normalized_correct = 0
    quantity_exact_correct = 0
    role_exact_correct = 0
    strict_line_correct = 0

    for key in matched_keys:
        expected = gold[key]
        actual = predicted[key]

        item_exact = actual.item_name_raw == expected.item_name_raw
        item_normalized = (
            _normalize_text(actual.item_name_raw)
            == _normalize_text(expected.item_name_raw)
        )
        unit_exact = actual.unit_raw == expected.unit_raw
        unit_normalized = (
            _normalize_text(actual.unit_raw)
            == _normalize_text(expected.unit_raw)
        )
        quantity_exact = actual.quantity == expected.quantity
        role_exact = actual.document_role == expected.document_role

        item_exact_correct += int(item_exact)
        item_normalized_correct += int(item_normalized)
        unit_exact_correct += int(unit_exact)
        unit_normalized_correct += int(unit_normalized)
        quantity_exact_correct += int(quantity_exact)
        role_exact_correct += int(role_exact)
        strict_line_correct += int(
            item_exact
            and unit_exact
            and quantity_exact
            and role_exact
        )

    documents_perfect = 0
    for document in gold_documents:
        expected_keys = {_line_key(line) for line in document.lines}
        actual_keys = {
            key
            for key in predicted
            if key[0] == document.document_id
        }
        if actual_keys != expected_keys:
            continue
        if all(
            predicted[key].item_name_raw == gold[key].item_name_raw
            and predicted[key].unit_raw == gold[key].unit_raw
            and predicted[key].quantity == gold[key].quantity
            and predicted[key].document_role == gold[key].document_role
            for key in expected_keys
        ):
            documents_perfect += 1

    return Stage1AEvaluation(
        documents_total=len(gold_documents),
        documents_perfect=documents_perfect,
        extraction_failures=extraction_failures,
        gold_lines=len(gold),
        predicted_lines=len(predicted),
        matched_locators=len(matched_keys),
        item_exact_correct=item_exact_correct,
        item_normalized_correct=item_normalized_correct,
        unit_exact_correct=unit_exact_correct,
        unit_normalized_correct=unit_normalized_correct,
        quantity_exact_correct=quantity_exact_correct,
        role_exact_correct=role_exact_correct,
        strict_line_correct=strict_line_correct,
    )
