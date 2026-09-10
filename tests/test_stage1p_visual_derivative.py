from __future__ import annotations

from pathlib import Path

from PIL import Image, PngImagePlugin
import pytest

from stroy_snab.anonymization import (
    NormalizedRedactionBox,
    build_public_manifest,
    rebuild_image_to_png,
    render_pdf_to_pngs,
    scan_path,
)


def test_image_rebuild_strips_metadata_and_redacts_pixels(tmp_path: Path):
    source = tmp_path / "private-source.png"
    output = tmp_path / "page-001.png"
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Author", "Secret Supplier")
    Image.new("RGB", (100, 100), "black").save(source, pnginfo=metadata)

    rebuild_image_to_png(
        source,
        output,
        redactions=[NormalizedRedactionBox(0.0, 0.0, 0.5, 0.5)],
    )

    with Image.open(output) as result:
        assert result.info == {}
        assert result.getpixel((10, 10)) == (255, 255, 255)
        assert result.getpixel((90, 90)) == (0, 0, 0)

    report = scan_path(output, forbidden_tokens=["Secret Supplier"])
    assert report.automated_checks_passed
    assert report.requires_manual_visual_review
    assert not report.passed


def test_image_source_is_never_overwritten(tmp_path: Path):
    source = tmp_path / "private.png"
    Image.new("RGB", (10, 10), "white").save(source)
    before = source.read_bytes()

    with pytest.raises(ValueError):
        rebuild_image_to_png(source, source)

    assert source.read_bytes() == before


def test_pdf_render_produces_only_new_metadata_free_png_pages(tmp_path: Path):
    source = tmp_path / "private.pdf"
    page1 = Image.new("RGB", (200, 300), "black")
    page2 = Image.new("RGB", (200, 300), "white")
    page1.save(source, format="PDF", save_all=True, append_images=[page2])
    output_dir = tmp_path / "visual"

    outputs = render_pdf_to_pngs(
        source,
        output_dir,
        redactions_by_page={0: [NormalizedRedactionBox(0.0, 0.0, 1.0, 0.5)]},
        dpi=72,
    )

    assert [path.name for path in outputs] == ["page-001.png", "page-002.png"]
    assert sorted(path.name for path in output_dir.iterdir()) == ["page-001.png", "page-002.png"]
    with Image.open(outputs[0]) as rendered:
        assert rendered.info == {}
        assert rendered.getpixel((100, 50)) == (255, 255, 255)
        assert rendered.getpixel((100, 250)) == (0, 0, 0)


def test_pdf_invalid_redaction_page_leaves_no_partial_output(tmp_path: Path):
    source = tmp_path / "private.pdf"
    Image.new("RGB", (200, 300), "white").save(source, format="PDF")
    output_dir = tmp_path / "visual"

    with pytest.raises(ValueError):
        render_pdf_to_pngs(
            source,
            output_dir,
            redactions_by_page={1: [NormalizedRedactionBox(0.0, 0.0, 1.0, 1.0)]},
        )

    assert not output_dir.exists()


def test_pdf_page_pixel_limit_fails_before_public_output(tmp_path: Path):
    source = tmp_path / "private.pdf"
    Image.new("RGB", (200, 300), "white").save(source, format="PDF")
    output_dir = tmp_path / "visual"

    with pytest.raises(ValueError):
        render_pdf_to_pngs(source, output_dir, dpi=240, max_page_pixels=100)

    assert not output_dir.exists()


def test_real_visual_manifest_requires_completed_manual_review():
    document = {
        "document_id": "INVOICE_0001",
        "role": "OFFER_OR_INVOICE",
        "format": "png",
        "derivative_files": ["INVOICE_0001/visual/page-001.png"],
        "manual_visual_review": False,
    }
    with pytest.raises(ValueError):
        build_public_manifest(
            case_id="CASE_0001",
            provenance="anonymized-real",
            documents=[document],
        )

    document["manual_visual_review"] = True
    manifest = build_public_manifest(
        case_id="CASE_0001",
        provenance="anonymized-real",
        documents=[document],
    )
    assert manifest["documents"][0]["manual_visual_review"] is True
