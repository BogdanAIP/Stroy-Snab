from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import os
import shutil
import tempfile
import warnings
from typing import Mapping, Sequence

from PIL import Image, ImageDraw, ImageOps
import pypdfium2 as pdfium


@dataclass(frozen=True)
class NormalizedRedactionBox:
    """A page/image redaction rectangle in normalized top-left coordinates."""

    left: float
    top: float
    right: float
    bottom: float

    def validate(self) -> "NormalizedRedactionBox":
        values = (self.left, self.top, self.right, self.bottom)
        if not all(isinstance(value, (int, float)) for value in values):
            raise TypeError("redaction coordinates must be numeric")
        if not all(math.isfinite(float(value)) and 0.0 <= float(value) <= 1.0 for value in values):
            raise ValueError("redaction coordinates must be finite and normalized to [0, 1]")
        if not float(self.left) < float(self.right) or not float(self.top) < float(self.bottom):
            raise ValueError("redaction box must have positive area")
        return self


def _pixel_box(box: NormalizedRedactionBox, width: int, height: int) -> tuple[int, int, int, int]:
    box.validate()
    left = max(0, min(width - 1, math.floor(float(box.left) * width)))
    top = max(0, min(height - 1, math.floor(float(box.top) * height)))
    right_exclusive = max(left + 1, min(width, math.ceil(float(box.right) * width)))
    bottom_exclusive = max(top + 1, min(height, math.ceil(float(box.bottom) * height)))
    return left, top, right_exclusive - 1, bottom_exclusive - 1


def _fresh_rgb_pixels(image: Image.Image, boxes: Sequence[NormalizedRedactionBox]) -> Image.Image:
    oriented = ImageOps.exif_transpose(image)
    rgb = oriented.convert("RGB")
    clean = Image.new("RGB", rgb.size, "white")
    clean.paste(rgb, (0, 0))
    draw = ImageDraw.Draw(clean)
    for box in boxes:
        draw.rectangle(_pixel_box(box, *clean.size), fill="white")
    return clean


def _save_png_atomic(image: Image.Image, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp.png", dir=output.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        # No source metadata/profile objects are forwarded to the new PNG.
        image.save(temp_path, format="PNG", compress_level=6)
        os.replace(temp_path, output)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    return output


def _validate_source(source: Path, *, max_source_bytes: int) -> None:
    if max_source_bytes < 1:
        raise ValueError("max_source_bytes must be positive")
    if not source.is_file():
        raise ValueError("source must be a regular file")
    if source.stat().st_size > max_source_bytes:
        raise ValueError("source exceeds Stage 1P byte limit")


def rebuild_image_to_png(
    source_path: str | Path,
    output_path: str | Path,
    *,
    redactions: Sequence[NormalizedRedactionBox] = (),
    max_source_bytes: int = 100 * 1024 * 1024,
    max_pixels: int = 25_000_000,
) -> Path:
    """Re-encode one source image into a fresh metadata-free RGB PNG.

    Redaction boxes are supplied by a private/manual process and are applied to
    pixels before publication. This function does not claim that all sensitive
    visible regions were identified; the resulting visual still requires the
    independent visual review recorded by the public manifest.
    """

    source = Path(source_path)
    output = Path(output_path)
    _validate_source(source, max_source_bytes=max_source_bytes)
    if max_pixels < 1:
        raise ValueError("max_pixels must be positive")
    if source.resolve() == output.resolve():
        raise ValueError("visual derivative must not overwrite its private source")

    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(source) as image:
            if getattr(image, "n_frames", 1) != 1:
                raise ValueError("multi-frame images are not accepted as Stage 1P visual sources")
            if image.width * image.height > max_pixels:
                raise ValueError("source image exceeds Stage 1P pixel limit")
            clean = _fresh_rgb_pixels(image, redactions)
    return _save_png_atomic(clean, output)


def render_pdf_to_pngs(
    source_path: str | Path,
    output_dir: str | Path,
    *,
    redactions_by_page: Mapping[int, Sequence[NormalizedRedactionBox]] | None = None,
    dpi: int = 144,
    max_source_bytes: int = 100 * 1024 * 1024,
    max_pages: int = 50,
    max_page_pixels: int = 25_000_000,
) -> list[Path]:
    """Rasterize a PDF serially into new metadata-free PNG pages.

    The original PDF object graph, text/OCR layers, attachments, forms and
    annotations are not copied into the public derivative. PDFium rendering is
    deliberately serial because PDFium is not thread-safe and the target is a
    bounded-memory 16 GB CPU-first workstation.
    """

    source = Path(source_path)
    out_dir = Path(output_dir)
    _validate_source(source, max_source_bytes=max_source_bytes)
    if not isinstance(dpi, int) or not 72 <= dpi <= 240:
        raise ValueError("dpi must be an integer between 72 and 240")
    if max_pages < 1 or max_page_pixels < 1:
        raise ValueError("resource limits must be positive")
    if out_dir.exists():
        raise FileExistsError("visual derivative output directory must not already exist")

    masks = redactions_by_page or {}
    if any(not isinstance(page_index, int) or page_index < 0 for page_index in masks):
        raise ValueError("redaction page indexes must be non-negative integers")

    out_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{out_dir.name}.", dir=out_dir.parent))
    scale = dpi / 72.0
    page_count = 0

    try:
        pdf = pdfium.PdfDocument(source)
        try:
            page_count = len(pdf)
            if page_count < 1:
                raise ValueError("PDF contains no pages")
            if page_count > max_pages:
                raise ValueError("PDF exceeds Stage 1P page limit")
            if any(page_index >= page_count for page_index in masks):
                raise ValueError("redaction references a page outside the PDF")

            for page_index in range(page_count):
                page = pdf[page_index]
                try:
                    width_pt, height_pt = page.get_size()
                    width_px = max(1, int(math.ceil(width_pt * scale)))
                    height_px = max(1, int(math.ceil(height_pt * scale)))
                    if width_px * height_px > max_page_pixels:
                        raise ValueError("rendered PDF page exceeds Stage 1P pixel limit")
                    bitmap = page.render(
                        scale=scale,
                        rev_byteorder=True,
                        fill_color=(255, 255, 255, 255),
                        may_draw_forms=False,
                        draw_annots=False,
                    )
                    try:
                        rendered = bitmap.to_pil()
                        clean = _fresh_rgb_pixels(rendered, masks.get(page_index, ()))
                    finally:
                        bitmap.close()
                finally:
                    page.close()
                _save_png_atomic(clean, temp_dir / f"page-{page_index + 1:03d}.png")
        finally:
            pdf.close()
        os.replace(temp_dir, out_dir)
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise

    return [out_dir / f"page-{page_index + 1:03d}.png" for page_index in range(page_count)]
