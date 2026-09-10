from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import platform
import sys
import tempfile
import time

from PIL import Image, ImageDraw

from stroy_snab.anonymization import (
    NormalizedRedactionBox,
    rebuild_image_to_png,
    render_pdf_to_pngs,
    write_sanitized_workbook,
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
        ok = psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb)
        if not ok:
            error = ctypes.get_last_error()
            raise OSError(error, "GetProcessMemoryInfo failed")
        return int(counters.PeakWorkingSetSize)

    import resource

    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return int(usage)
    return int(usage * 1024)


def _tree_bytes(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def _make_pdf(path: Path) -> None:
    pages: list[Image.Image] = []
    try:
        for page_index in range(3):
            image = Image.new("RGB", (1240, 1754), "white")
            draw = ImageDraw.Draw(image)
            for row in range(18):
                y = 80 + row * 80
                draw.rectangle((80, y, 1160, y + 2), fill="black")
            draw.rectangle((80, 80, 1160, 1660), outline="black", width=3)
            draw.rectangle((100, 120 + page_index * 20, 520, 210 + page_index * 20), fill="black")
            pages.append(image)
        pages[0].save(
            path,
            format="PDF",
            save_all=True,
            append_images=pages[1:],
            resolution=150.0,
        )
    finally:
        for image in pages:
            image.close()


def _make_jpeg(path: Path) -> None:
    image = Image.new("RGB", (1800, 2400), "white")
    try:
        draw = ImageDraw.Draw(image)
        for row in range(24):
            y = 100 + row * 85
            draw.rectangle((100, y, 1700, y + 3), fill="black")
        draw.rectangle((120, 140, 700, 360), fill="black")
        image.save(path, format="JPEG", quality=90)
    finally:
        image.close()


def run() -> dict[str, object]:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="stroy-snab-stage1p-benchmark-") as temp:
        root = Path(temp)

        rows = [["№", "Наименование", "Количество", "Ед."]]
        rows.extend([[index, f"Кабель тип {index % 50}", (index % 100) + 1, "м"] for index in range(1, 5001)])
        write_sanitized_workbook(
            root / "document.xlsx",
            sheets=[{"name": "REQUEST", "rows": rows}],
            forbidden_tokens=[],
        )

        pdf_path = root / "source.pdf"
        _make_pdf(pdf_path)
        pdf_outputs = render_pdf_to_pngs(
            pdf_path,
            root / "pdf-visual",
            redactions_by_page={0: [NormalizedRedactionBox(0.05, 0.05, 0.45, 0.18)]},
            dpi=144,
        )

        jpg_path = root / "source.jpg"
        _make_jpeg(jpg_path)
        rebuild_image_to_png(
            jpg_path,
            root / "image-visual.png",
            redactions=[NormalizedRedactionBox(0.05, 0.05, 0.45, 0.18)],
        )

        elapsed = time.perf_counter() - started
        result = {
            "schema_version": "1.0",
            "platform": platform.system(),
            "python": platform.python_version(),
            "xlsx_rows": 5001,
            "pdf_pages": len(pdf_outputs),
            "elapsed_seconds": round(elapsed, 3),
            "peak_rss_mb": round(_peak_rss_bytes() / (1024 * 1024), 1),
            "temporary_tree_mb": round(_tree_bytes(root) / (1024 * 1024), 1),
        }
    return result


if __name__ == "__main__":
    print("STAGE1P_BENCHMARK_JSON=" + json.dumps(run(), sort_keys=True))
