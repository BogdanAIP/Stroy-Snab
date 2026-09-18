from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import pypdfium2 as pdfium


class PdfNativeTextExtractionError(RuntimeError):
    """Raised when the native Stage 1A PDF baseline cannot safely read a PDF."""


_PROVIDER = "pypdfium2"
_PROVIDER_CONFIG_ID = "pdfium-native-text-sequential-v1"
_NEUTRAL_DOCUMENT_ID = re.compile(
    r"^(?:REQUEST|SPECIFICATION|OFFER_OR_INVOICE|UPD_OR_DELIVERY|INCOMING_CONTROL|DOCUMENT)_\d{4}$"
)
_SAFE_WARNING_CODES = frozenset({"NO_NATIVE_TEXT", "ROTATED_PAGE"})
_ALLOWED_BLOCK_KINDS = frozenset({"text", "table", "cell"})


@dataclass(frozen=True, slots=True)
class TextBlockEvidence:
    text: str
    bbox: tuple[float, float, float, float] | None = None
    confidence: float | None = None
    block_kind: str = "text"

    def __post_init__(self) -> None:
        if not self.text:
            raise ValueError("text block must not be empty")
        if self.block_kind not in _ALLOWED_BLOCK_KINDS:
            raise ValueError("unsupported block_kind")
        if self.confidence is not None and not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be between 0 and 1")
        if self.bbox is not None:
            if len(self.bbox) != 4:
                raise ValueError("bbox must contain four coordinates")
            if not all(isinstance(value, (int, float)) for value in self.bbox):
                raise ValueError("bbox coordinates must be numeric")


@dataclass(frozen=True, slots=True)
class DocumentPageEvidence:
    document_id: str
    page_number: int
    provider: str
    provider_config_id: str
    text_blocks: tuple[TextBlockEvidence, ...]
    tables: tuple[tuple[TextBlockEvidence, ...], ...] = ()
    warnings: tuple[str, ...] = ()
    rotation_degrees: int = 0

    def __post_init__(self) -> None:
        if not _NEUTRAL_DOCUMENT_ID.fullmatch(self.document_id):
            raise ValueError("document_id must be a reviewed neutral id")
        if self.page_number < 1:
            raise ValueError("page_number must be 1-based")
        if not self.provider or not self.provider_config_id:
            raise ValueError("provider identity must be explicit")
        if self.rotation_degrees not in {0, 90, 180, 270}:
            raise ValueError("rotation_degrees must be a PDF quarter-turn")
        if any(code not in _SAFE_WARNING_CODES for code in self.warnings):
            raise ValueError("warning must use a reviewed safe code")

    @property
    def source_locator(self) -> str:
        return f"PDF!p={self.page_number}"


@dataclass(frozen=True, slots=True)
class NativePdfProviderIdentity:
    provider: str
    provider_config_id: str
    pypdfium2_version: str
    pdfium_version: str
    concurrency: str


def native_pdf_provider_identity() -> NativePdfProviderIdentity:
    """Return exact runtime identity for reproducible experiment evidence."""

    return NativePdfProviderIdentity(
        provider=_PROVIDER,
        provider_config_id=_PROVIDER_CONFIG_ID,
        pypdfium2_version=str(pdfium.PYPDFIUM_INFO),
        pdfium_version=str(pdfium.PDFIUM_INFO),
        concurrency="sequential",
    )


def _normalize_page_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def _safe_close(resource: object | None) -> None:
    if resource is None:
        return
    close = getattr(resource, "close", None)
    if close is not None:
        close()


def extract_native_pdf_pages(
    path: str | Path,
    *,
    document_id: str,
) -> tuple[DocumentPageEvidence, ...]:
    """Extract provider-neutral page evidence from a digital PDF text layer.

    This is deliberately a weak Stage 1A experiment baseline. PDFium calls are
    sequential, no OCR/layout model is invoked, raw filenames never enter
    evidence locators, and provider errors are converted to safe error codes.
    """

    if not _NEUTRAL_DOCUMENT_ID.fullmatch(document_id):
        raise ValueError("document_id must be a reviewed neutral id")

    try:
        pdf = pdfium.PdfDocument(Path(path))
    except Exception:
        raise PdfNativeTextExtractionError("PDF_OPEN_FAILED") from None

    pages: list[DocumentPageEvidence] = []
    try:
        try:
            page_count = len(pdf)
        except Exception:
            raise PdfNativeTextExtractionError("PDF_PAGE_COUNT_FAILED") from None

        if page_count == 0:
            raise PdfNativeTextExtractionError("PDF_EMPTY_DOCUMENT")

        for page_index in range(page_count):
            page = None
            text_page = None
            try:
                page = pdf[page_index]
                rotation = int(page.get_rotation()) % 360
                text_page = page.get_textpage()
                text = _normalize_page_text(
                    text_page.get_text_bounded(errors="strict")
                )
            except Exception:
                raise PdfNativeTextExtractionError("PDF_NATIVE_TEXT_FAILED") from None
            finally:
                _safe_close(text_page)
                _safe_close(page)

            warnings: list[str] = []
            if rotation:
                warnings.append("ROTATED_PAGE")
            if not text:
                warnings.append("NO_NATIVE_TEXT")

            blocks = (
                (TextBlockEvidence(text=text),)
                if text
                else ()
            )
            pages.append(
                DocumentPageEvidence(
                    document_id=document_id,
                    page_number=page_index + 1,
                    provider=_PROVIDER,
                    provider_config_id=_PROVIDER_CONFIG_ID,
                    text_blocks=blocks,
                    warnings=tuple(warnings),
                    rotation_degrees=rotation,
                )
            )
    finally:
        _safe_close(pdf)

    return tuple(pages)
