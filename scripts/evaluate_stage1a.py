from __future__ import annotations

import argparse
import json
from pathlib import Path

from stroy_snab.evaluation.stage1a import evaluate_stage1a, load_gold_documents
from stroy_snab.experiments.stage1a_xlsx import (
    ProcurementLine,
    XlsxLineExtractionError,
    extract_xlsx_lines,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOLD = ROOT / "data" / "gold" / "stage1a" / "public_anonymized_real.json"


def _resolve_document_path(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return root / path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--dataset-label",
        default="public_anonymized_real",
        help="Opaque/safe label printed in aggregate output.",
    )
    args = parser.parse_args()

    gold_documents = load_gold_documents(args.gold)
    predictions: list[ProcurementLine] = []
    extraction_failures = 0

    for document in gold_documents:
        try:
            lines = extract_xlsx_lines(
                _resolve_document_path(args.root, document.path),
                document_id=document.document_id,
                document_role=document.document_role,
            )
        except (XlsxLineExtractionError, OSError, ValueError):
            extraction_failures += 1
            continue
        predictions.extend(lines)

    evaluation = evaluate_stage1a(
        gold_documents,
        predictions,
        extraction_failures=extraction_failures,
    )

    payload = {
        "experiment": "stage1a_xlsx_evaluation",
        "dataset": args.dataset_label,
        **evaluation.as_metrics(),
        "content_logged": False,
        "paths_logged": False,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))

    if extraction_failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
