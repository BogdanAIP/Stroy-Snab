from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

import pypdfium2 as pdfium


class PdfNativeTextExtractionError(RuntimeError):
    """Raised when the native Stage 1A PDF baseline cannot safely read a PDF."""


_PROVIDER = "pypdfium2"
_PROVIDER_CONFIG_ID = "pdfium-native-text-sequential-v1"
_NEUTRAL_DOCUMENT_ID = re.compile(
    r"^(?:REQUEST|SPECIFICATION|OFFER|INVOICE|DELIVERY|CONTROL|OFFER_OR_INVOICE|UPD_OR_DELIVERY|INCOMING_CONTROL|DOCUMENT)_\d{4}$"
)
_SAFE_WARNING_CODES = frozenset({"NO_NATIVE_TEXT", "ROTATED_PAGE"})
_ALLOWED_BLOCK_KINDS = frozenset({"text", "table", "cell"})
_MAX_SOURCE_BYTES = 100 * 1024 * 1024
_MAX_PAGES = 50
_MAX_PAGE_CHARACTERS = 1_000_000
_PROVIDER_ID = re.compile(r"^[a-z0-9][a-z0-9._/-]{0,63}$")
_PROVIDER_CONFIG_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")


@dataclass(frozen=True, slots=True)
class TextBlockEvidence:
    text: str = field(repr=False)
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
    text_blocks: tuple[TextBlockEvidence, ...] = field(repr=False)
    tables: tuple[tuple[TextBlockEvidence, ...], ...] = field(default=(), repr=False)
    warnings: tuple[str, ...] = ()
    rotation_degrees: int = 0

    def __post_init__(self) -> None:
        if not _NEUTRAL_DOCUMENT_ID.fullmatch(self.document_id):
            raise ValueError("document_id must be a reviewed neutral id")
        if self.page_number < 1:
            raise ValueError("page_number must be 1-based")
        if not _PROVIDER_ID.fullmatch(self.provider):
            raise ValueError("provider must be a safe identifier")
        if not _PROVIDER_CONFIG_ID_PATTERN.fullmatch(self.provider_config_id):
            raise ValueError("provider_config_id must be a safe identifier")
        if any(not isinstance(block, TextBlockEvidence) for block in self.text_blocks):
            raise ValueError("text_blocks must contain provider-neutral TextBlockEvidence")
        if any(
            not isinstance(block, TextBlockEvidence)
            for table in self.tables
            for block in table
        ):
            raise ValueError("tables must contain provider-neutral TextBlockEvidence")
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
        try:
            close()
        except Exception:
            raise PdfNativeTextExtractionError("PDF_RESOURCE_CLOSE_FAILED") from None


def extract_native_pdf_pages(
    path: str | Path,
    *,
    document_id: str,
    max_source_bytes: int = _MAX_SOURCE_BYTES,
    max_pages: int = _MAX_PAGES,
    max_page_characters: int = _MAX_PAGE_CHARACTERS,
) -> tuple[DocumentPageEvidence, ...]:
    """Extract provider-neutral page evidence from a digital PDF text layer.

    This is deliberately a weak Stage 1A experiment baseline. PDFium calls are
    sequential, no OCR/layout model is invoked, raw filenames never enter
    evidence locators, and provider errors are converted to safe error codes.
    """

    if not _NEUTRAL_DOCUMENT_ID.fullmatch(document_id):
        raise ValueError("document_id must be a reviewed neutral id")
    limits = (
        ("max_source_bytes", max_source_bytes, _MAX_SOURCE_BYTES),
        ("max_pages", max_pages, _MAX_PAGES),
        ("max_page_characters", max_page_characters, _MAX_PAGE_CHARACTERS),
    )
    for name, value, ceiling in limits:
        if value < 1 or value > ceiling:
            raise ValueError(f"{name} must be between 1 and {ceiling}")

    source = Path(path)
    try:
        if source.stat().st_size > max_source_bytes:
            raise PdfNativeTextExtractionError("PDF_SOURCE_LIMIT_EXCEEDED")
        with source.open("rb") as handle:
            source_bytes = handle.read(max_source_bytes + 1)
        if len(source_bytes) > max_source_bytes:
            raise PdfNativeTextExtractionError("PDF_SOURCE_LIMIT_EXCEEDED")
    except PdfNativeTextExtractionError:
        raise
    except Exception:
        raise PdfNativeTextExtractionError("PDF_OPEN_FAILED") from None

    try:
        # Bytes are deliberate: pypdfium2 PdfDocument repr for byte input is
        # path-neutral, so DEBUG_AUTOCLOSE cannot echo the raw source pathname.
        pdf = pdfium.PdfDocument(source_bytes)
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
        if page_count > max_pages:
            raise PdfNativeTextExtractionError("PDF_PAGE_LIMIT_EXCEEDED")

        for page_index in range(page_count):
            page = None
            text_page = None
            try:
                page = pdf[page_index]
                rotation = int(page.get_rotation()) % 360
                text_page = page.get_textpage()
                character_count = int(text_page.count_chars())
                if character_count > max_page_characters:
                    raise PdfNativeTextExtractionError("PDF_TEXT_LIMIT_EXCEEDED")
                text = _normalize_page_text(
                    text_page.get_text_bounded(errors="strict")
                )
            except PdfNativeTextExtractionError:
                raise
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
