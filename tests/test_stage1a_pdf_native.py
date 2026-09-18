from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw
import pytest

from stroy_snab.experiments.stage1a_pdf import (
    PdfNativeTextExtractionError,
    extract_native_pdf_pages,
    native_pdf_provider_identity,
)
from stroy_snab.experiments.stage1a_pdf_synthetic import (
    SyntheticPdfPage,
    write_synthetic_text_pdf,
)


def test_extracts_unicode_text_layer_into_provider_neutral_page_evidence(
    tmp_path: Path,
) -> None:
    path = tmp_path / "synthetic.pdf"
    write_synthetic_text_pdf(
        path,
        pages=[
            SyntheticPdfPage(
                lines=(
                    "Наименование | Ед. | Количество",
                    "Кабель ВВГнг(А)-LS 3x2,5 | м | 50",
                    "Смесь сухая | кг | 1 200,5",
                )
            )
        ],
    )

    pages = extract_native_pdf_pages(path, document_id="DOCUMENT_0001")

    assert len(pages) == 1
    page = pages[0]
    assert page.document_id == "DOCUMENT_0001"
    assert page.page_number == 1
    assert page.provider == "pypdfium2"
    assert page.provider_config_id == "pdfium-native-text-sequential-v1"
    assert page.source_locator == "PDF!p=1"
    assert page.rotation_degrees == 0
    assert page.warnings == ()
    assert page.tables == ()
    assert len(page.text_blocks) == 1
    assert page.text_blocks[0].bbox is None
    assert page.text_blocks[0].confidence is None
    assert page.text_blocks[0].block_kind == "text"
    assert "Кабель ВВГнг(А)-LS 3x2,5" in page.text_blocks[0].text
    assert "1 200,5" in page.text_blocks[0].text


def test_multi_page_source_locators_never_embed_raw_filename(tmp_path: Path) -> None:
    private_looking_name = "SUPPLIER_SECRET_INVOICE_777.pdf"
    path = tmp_path / private_looking_name
    write_synthetic_text_pdf(
        path,
        pages=[
            SyntheticPdfPage(lines=("Item A | pcs | 2",)),
            SyntheticPdfPage(lines=("Item B | m | 10",)),
        ],
    )

    pages = extract_native_pdf_pages(path, document_id="DOCUMENT_0002")

    assert [page.source_locator for page in pages] == ["PDF!p=1", "PDF!p=2"]
    assert all(private_looking_name not in page.source_locator for page in pages)


def test_rotated_page_is_explicitly_marked_without_hiding_native_order(
    tmp_path: Path,
) -> None:
    path = tmp_path / "rotated.pdf"
    write_synthetic_text_pdf(
        path,
        pages=[
            SyntheticPdfPage(
                lines=("Header Item Unit Qty", "Cable m 50"),
                rotation_degrees=90,
            )
        ],
    )

    page = extract_native_pdf_pages(path, document_id="DOCUMENT_0003")[0]

    assert page.rotation_degrees == 90
    assert page.warnings == ("ROTATED_PAGE",)
    text = page.text_blocks[0].text
    assert "Header Item Unit Qty" in text
    assert "Cable m 50" in text


def test_image_only_pdf_is_reported_as_no_native_text(tmp_path: Path) -> None:
    path = tmp_path / "scan.pdf"
    image = Image.new("RGB", (600, 800), "white")
    try:
        draw = ImageDraw.Draw(image)
        draw.rectangle((50, 100, 550, 650), outline="black", width=3)
        image.save(path, format="PDF", resolution=150.0)
    finally:
        image.close()

    page = extract_native_pdf_pages(path, document_id="DOCUMENT_0004")[0]

    assert page.text_blocks == ()
    assert page.warnings == ("NO_NATIVE_TEXT",)
    assert page.source_locator == "PDF!p=1"


def test_corrupt_pdf_fails_closed_without_echoing_private_path(tmp_path: Path) -> None:
    path = tmp_path / "PRIVATE_SUPPLIER_SECRET.pdf"
    path.write_bytes(b"not a pdf")

    with pytest.raises(PdfNativeTextExtractionError) as exc_info:
        extract_native_pdf_pages(path, document_id="DOCUMENT_0005")

    assert str(exc_info.value) == "PDF_OPEN_FAILED"
    assert "PRIVATE_SUPPLIER_SECRET" not in str(exc_info.value)


def test_raw_looking_document_id_is_rejected_before_extraction(tmp_path: Path) -> None:
    path = tmp_path / "unused.pdf"
    path.write_bytes(b"not needed")

    with pytest.raises(ValueError, match="reviewed neutral id"):
        extract_native_pdf_pages(path, document_id="Supplier Alpha invoice 123.pdf")


def test_provider_identity_records_exact_runtime_versions() -> None:
    identity = native_pdf_provider_identity()

    assert identity.provider == "pypdfium2"
    assert identity.provider_config_id == "pdfium-native-text-sequential-v1"
    assert identity.pypdfium2_version
    assert identity.pdfium_version
    assert identity.concurrency == "sequential"
