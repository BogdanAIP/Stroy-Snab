from __future__ import annotations

from pathlib import Path
import inspect
import subprocess
import sys

from PIL import Image, ImageDraw
import pytest

import stroy_snab.experiments.stage1a_pdf as stage1a_pdf
from stroy_snab.experiments.stage1a_pdf import (
    DocumentPageEvidence,
    PdfNativeTextExtractionError,
    TextBlockEvidence,
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


def test_stage1p_style_neutral_document_ids_remain_accepted(tmp_path: Path) -> None:
    path = tmp_path / "invoice.pdf"
    write_synthetic_text_pdf(
        path,
        pages=[SyntheticPdfPage(lines=("Item | pcs | 1",))],
    )

    page = extract_native_pdf_pages(path, document_id="INVOICE_0001")[0]

    assert page.document_id == "INVOICE_0001"
    assert page.source_locator == "PDF!p=1"


def test_evidence_repr_does_not_echo_document_text() -> None:
    secret = "PRIVATE_PROCUREMENT_TEXT_SHOULD_NOT_BE_LOGGED"
    block = TextBlockEvidence(text=secret)
    page = DocumentPageEvidence(
        document_id="DOCUMENT_0006",
        page_number=1,
        provider="pypdfium2",
        provider_config_id="pdfium-native-text-sequential-v1",
        text_blocks=(block,),
    )

    assert secret not in repr(block)
    assert secret not in repr(page)


def test_page_contract_rejects_provider_specific_objects_and_unsafe_ids() -> None:
    block = TextBlockEvidence(text="safe")

    with pytest.raises(ValueError, match="provider must be a safe identifier"):
        DocumentPageEvidence(
            document_id="DOCUMENT_0006",
            page_number=1,
            provider="private supplier path",
            provider_config_id="safe-config",
            text_blocks=(block,),
        )

    with pytest.raises(ValueError, match="provider-neutral"):
        DocumentPageEvidence(
            document_id="DOCUMENT_0006",
            page_number=1,
            provider="pypdfium2",
            provider_config_id="safe-config",
            text_blocks=(block,),
            tables=((object(),),),  # type: ignore[arg-type]
        )


def test_pdfium_autoclose_debug_stderr_never_contains_raw_source_path(
    tmp_path: Path,
) -> None:
    private_looking_name = "PRIVATE_SUPPLIER_SECRET_INVOICE_777.pdf"
    path = tmp_path / private_looking_name
    write_synthetic_text_pdf(
        path,
        pages=[SyntheticPdfPage(lines=("Item | pcs | 1",))],
    )

    script = """
import logging
import sys
import pypdfium2_cfg
from stroy_snab.experiments.stage1a_pdf import extract_native_pdf_pages

pypdfium2_cfg.DEBUG_AUTOCLOSE.value = logging.DEBUG
extract_native_pdf_pages(sys.argv[1], document_id="DOCUMENT_0010")
"""
    completed = subprocess.run(
        [sys.executable, "-c", script, str(path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Close (explicit)" in completed.stderr
    assert private_looking_name not in completed.stderr
    assert str(path) not in completed.stderr
    assert "Item | pcs | 1" not in completed.stderr


def test_production_resource_defaults_are_locked() -> None:
    parameters = inspect.signature(extract_native_pdf_pages).parameters

    assert parameters["max_source_bytes"].default == 100 * 1024 * 1024
    assert parameters["max_pages"].default == 50
    assert parameters["max_page_characters"].default == 1_000_000


@pytest.mark.parametrize(
    ("argument", "value"),
    [
        ("max_source_bytes", 100 * 1024 * 1024 + 1),
        ("max_pages", 51),
        ("max_page_characters", 1_000_001),
    ],
)
def test_resource_hard_ceiling_cannot_be_raised(
    tmp_path: Path,
    argument: str,
    value: int,
) -> None:
    path = tmp_path / "bounded.pdf"
    write_synthetic_text_pdf(
        path,
        pages=[SyntheticPdfPage(lines=("Item | pcs | 1",))],
    )

    with pytest.raises(ValueError, match=argument):
        extract_native_pdf_pages(
            path,
            document_id="DOCUMENT_0011",
            **{argument: value},
        )


def test_source_size_limit_fails_closed_without_echoing_path(tmp_path: Path) -> None:
    path = tmp_path / "PRIVATE_OVERSIZE_SUPPLIER.pdf"
    write_synthetic_text_pdf(
        path,
        pages=[SyntheticPdfPage(lines=("Item | pcs | 1",))],
    )

    with pytest.raises(PdfNativeTextExtractionError) as exc_info:
        extract_native_pdf_pages(
            path,
            document_id="DOCUMENT_0007",
            max_source_bytes=1,
        )

    assert str(exc_info.value) == "PDF_SOURCE_LIMIT_EXCEEDED"
    assert "PRIVATE_OVERSIZE_SUPPLIER" not in str(exc_info.value)


def test_page_limit_fails_closed_before_page_extraction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "many-pages.pdf"
    path.write_bytes(b"%PDF-1.4\n")

    class FakePdf:
        page_accessed = False

        def __len__(self) -> int:
            return 2

        def __getitem__(self, index: int):
            self.page_accessed = True
            raise AssertionError("page access must not occur before page-limit rejection")

        def close(self) -> None:
            pass

    fake_pdf = FakePdf()
    monkeypatch.setattr(stage1a_pdf.pdfium, "PdfDocument", lambda source: fake_pdf)

    with pytest.raises(PdfNativeTextExtractionError) as exc_info:
        extract_native_pdf_pages(
            path,
            document_id="DOCUMENT_0008",
            max_pages=1,
        )

    assert str(exc_info.value) == "PDF_PAGE_LIMIT_EXCEEDED"
    assert fake_pdf.page_accessed is False


def test_text_character_limit_fails_closed_before_materializing_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "dense-text.pdf"
    path.write_bytes(b"%PDF-1.4\n")

    class FakeTextPage:
        count_called = False
        bounded_called = False

        def count_chars(self) -> int:
            self.count_called = True
            return 10

        def get_text_bounded(self, *, errors: str) -> str:
            self.bounded_called = True
            raise AssertionError("text must not materialize after character-limit rejection")

        def close(self) -> None:
            pass

    class FakePage:
        def __init__(self, text_page: FakeTextPage) -> None:
            self.text_page = text_page

        def get_rotation(self) -> int:
            return 0

        def get_textpage(self) -> FakeTextPage:
            return self.text_page

        def close(self) -> None:
            pass

    class FakePdf:
        def __init__(self, page: FakePage) -> None:
            self.page = page

        def __len__(self) -> int:
            return 1

        def __getitem__(self, index: int) -> FakePage:
            return self.page

        def close(self) -> None:
            pass

    fake_text_page = FakeTextPage()
    fake_pdf = FakePdf(FakePage(fake_text_page))
    monkeypatch.setattr(stage1a_pdf.pdfium, "PdfDocument", lambda source: fake_pdf)

    with pytest.raises(PdfNativeTextExtractionError) as exc_info:
        extract_native_pdf_pages(
            path,
            document_id="DOCUMENT_0009",
            max_page_characters=5,
        )

    assert str(exc_info.value) == "PDF_TEXT_LIMIT_EXCEEDED"
    assert fake_text_page.count_called is True
    assert fake_text_page.bounded_called is False


def test_provider_identity_records_exact_runtime_versions() -> None:
    identity = native_pdf_provider_identity()

    assert identity.provider == "pypdfium2"
    assert identity.provider_config_id == "pdfium-native-text-sequential-v1"
    assert identity.pypdfium2_version
    assert identity.pdfium_version
    assert identity.concurrency == "sequential"
