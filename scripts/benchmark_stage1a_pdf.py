from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import platform
import sys
import tempfile
from time import perf_counter

from stroy_snab.experiments.stage1a_pdf import (
    extract_native_pdf_pages,
    native_pdf_provider_identity,
)
from stroy_snab.experiments.stage1a_pdf_synthetic import (
    SyntheticPdfPage,
    write_synthetic_text_pdf,
)


def _peak_rss_bytes() -> int:
    if sys.platform == "win32":
        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.argtypes = []
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
            wintypes.DWORD,
        ]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(counters)
        process = kernel32.GetCurrentProcess()
        if not psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb):
            raise OSError(ctypes.get_last_error(), "GetProcessMemoryInfo failed")
        return int(counters.PeakWorkingSetSize)

    import resource

    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return int(usage)
    return int(usage * 1024)


def _tree_bytes(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def run() -> dict[str, object]:
    identity = native_pdf_provider_identity()
    with tempfile.TemporaryDirectory(prefix="stroy-snab-stage1a-pdf-") as temp:
        root = Path(temp)
        path = root / "synthetic.pdf"
        write_synthetic_text_pdf(
            path,
            pages=[
                SyntheticPdfPage(
                    lines=(
                        "Наименование | Ед. | Количество",
                        "Кабель ВВГнг(А)-LS 3x2,5 | м | 50",
                    )
                ),
                SyntheticPdfPage(
                    lines=(
                        "Наименование | Ед. | Количество",
                        "Смесь сухая | кг | 1 200,5",
                    )
                ),
                SyntheticPdfPage(
                    lines=("Rotated baseline row | pcs | 4",),
                    rotation_degrees=90,
                ),
            ],
        )

        started = perf_counter()
        pages = extract_native_pdf_pages(path, document_id="DOCUMENT_0001")
        elapsed_ms = (perf_counter() - started) * 1000
        characters = sum(
            len(block.text)
            for page in pages
            for block in page.text_blocks
        )
        rotated_pages = sum(bool(page.rotation_degrees) for page in pages)
        empty_native_text_pages = sum(not page.text_blocks for page in pages)
        temporary_tree_mb = round(_tree_bytes(root) / (1024 * 1024), 3)

    return {
        "schema_version": "1.0",
        "experiment": "stage1a_pdf_native_text_baseline",
        "dataset": "synthetic",
        "platform": platform.system(),
        "python": platform.python_version(),
        "provider": identity.provider,
        "provider_config_id": identity.provider_config_id,
        "pypdfium2_version": identity.pypdfium2_version,
        "pdfium_version": identity.pdfium_version,
        "concurrency": identity.concurrency,
        "documents_processed": 1,
        "pages_processed": len(pages),
        "characters_extracted": characters,
        "rotated_pages": rotated_pages,
        "empty_native_text_pages": empty_native_text_pages,
        "elapsed_ms": round(elapsed_ms, 3),
        "peak_rss_mb": round(_peak_rss_bytes() / (1024 * 1024), 1),
        "temporary_tree_mb": temporary_tree_mb,
        "content_logged": False,
        "paths_logged": False,
        "model_footprint_mb": 0.0,
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True))
