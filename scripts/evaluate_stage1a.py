from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from stroy_snab.evaluation.stage1a import evaluate_stage1a, load_gold_documents
from stroy_snab.experiments.stage1a_xlsx import ProcurementLine, extract_xlsx_lines


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOLD = ROOT / "data" / "gold" / "stage1a" / "public_anonymized_real.json"
_SAFE_DATASET_LABEL = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")


def _resolve_document_path(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return root / path


def _safe_error_payload(dataset_label: str) -> dict[str, object]:
    return {
        "experiment": "stage1a_xlsx_evaluation",
        "dataset": dataset_label,
        "evaluation_status": "ERROR",
        "content_logged": False,
        "paths_logged": False,
    }


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

    if _SAFE_DATASET_LABEL.fullmatch(args.dataset_label) is None:
        print(
            json.dumps(
                _safe_error_payload("INVALID_DATASET_LABEL"),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        raise SystemExit(2)

    try:
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
            except Exception:
                extraction_failures += 1
                continue
            predictions.extend(lines)

        evaluation = evaluate_stage1a(
            gold_documents,
            predictions,
            extraction_failures=extraction_failures,
        )
    except Exception:
        print(
            json.dumps(
                _safe_error_payload(args.dataset_label),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        raise SystemExit(2)

    payload = {
        "experiment": "stage1a_xlsx_evaluation",
        "dataset": args.dataset_label,
        "evaluation_status": "PASS" if extraction_failures == 0 else "FAIL",
        **evaluation.as_metrics(),
        "content_logged": False,
        "paths_logged": False,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))

    if extraction_failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
