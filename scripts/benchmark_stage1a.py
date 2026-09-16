from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

from stroy_snab.experiments.stage1a_xlsx import extract_xlsx_lines


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "data" / "fixtures" / "documents" / "anonymized-real"


def main() -> None:
    manifests = sorted(FIXTURE_ROOT.glob("CASE_*/manifest.json"))
    if not manifests:
        raise SystemExit("no anonymized-real manifests found")

    document_count = 0
    line_count = 0
    started = perf_counter()

    for manifest_path in manifests:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        case_dir = manifest_path.parent

        for document in manifest["documents"]:
            if document["format"] != "xlsx":
                continue

            xlsx_files = [
                case_dir / relative_name
                for relative_name in document["derivative_files"]
                if relative_name.lower().endswith(".xlsx")
            ]
            for path in xlsx_files:
                lines = extract_xlsx_lines(
                    path,
                    document_id=document["document_id"],
                    document_role=document["role"],
                )
                document_count += 1
                line_count += len(lines)

    if document_count == 0:
        raise SystemExit("no XLSX documents found in anonymized-real fixtures")
    if line_count == 0:
        raise SystemExit("XLSX baseline extracted zero lines")

    elapsed_ms = (perf_counter() - started) * 1000
    print(
        json.dumps(
            {
                "experiment": "stage1a_xlsx_baseline",
                "dataset": "public_anonymized_real",
                "documents_processed": document_count,
                "lines_extracted": line_count,
                "elapsed_ms": round(elapsed_ms, 3),
                "content_logged": False,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
