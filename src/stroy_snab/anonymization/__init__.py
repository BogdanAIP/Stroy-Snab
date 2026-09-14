"""Stage 1P anonymization primitives."""

from .ids import NeutralIdAllocator
from .leakcheck import LeakFinding, LeakReport, scan_path, scan_text
from .manifest import build_public_manifest, validate_public_manifest
from .visual_derivative import NormalizedRedactionBox, rebuild_image_to_png, render_pdf_to_pngs
from .xlsx_rebuild import write_sanitized_workbook

__all__ = [
    "LeakFinding",
    "LeakReport",
    "NeutralIdAllocator",
    "NormalizedRedactionBox",
    "build_public_manifest",
    "rebuild_image_to_png",
    "render_pdf_to_pngs",
    "scan_path",
    "scan_text",
    "validate_public_manifest",
    "write_sanitized_workbook",
]
