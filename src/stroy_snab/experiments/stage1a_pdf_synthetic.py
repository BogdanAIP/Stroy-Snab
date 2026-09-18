from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True, slots=True)
class SyntheticPdfPage:
    lines: tuple[str, ...]
    rotation_degrees: int = 0

    def __post_init__(self) -> None:
        if not self.lines:
            raise ValueError("synthetic PDF page must contain at least one line")
        if self.rotation_degrees not in {0, 90, 180, 270}:
            raise ValueError("rotation_degrees must be a PDF quarter-turn")


def _encode_text(
    text: str,
    *,
    unicode_codes: dict[str, int],
) -> bytes:
    encoded = bytearray()
    for character in text:
        codepoint = ord(character)
        if codepoint < 128:
            encoded.append(codepoint)
            continue
        code = unicode_codes.get(character)
        if code is None:
            code = 0x80 + len(unicode_codes)
            if code > 0xFF:
                raise ValueError("synthetic fixture uses too many non-ASCII characters")
            unicode_codes[character] = code
        encoded.append(code)
    return bytes(encoded)


def _cmap_bytes(unicode_codes: dict[str, int]) -> bytes:
    mappings = [
        f"<{code:02X}> <{ord(character):04X}>"
        for character, code in sorted(unicode_codes.items(), key=lambda pair: pair[1])
    ]
    body = "\n".join(mappings)
    return (
        "/CIDInit /ProcSet findresource begin\n"
        "12 dict begin\n"
        "begincmap\n"
        "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n"
        "/CMapName /StroySnabSyntheticToUnicode def\n"
        "/CMapType 2 def\n"
        "1 begincodespacerange\n"
        "<00> <FF>\n"
        "endcodespacerange\n"
        f"{len(mappings)} beginbfchar\n"
        f"{body}\n"
        "endbfchar\n"
        "endcmap\n"
        "CMapName currentdict /CMap defineresource pop\n"
        "end\n"
        "end\n"
    ).encode("ascii")


def write_synthetic_text_pdf(
    path: str | Path,
    *,
    pages: Sequence[SyntheticPdfPage],
) -> Path:
    """Write a tiny deterministic PDF with a Unicode text layer for tests/evals.

    The generator exists only for public synthetic experiment fixtures; it is not
    a document-production component.
    """

    if not pages:
        raise ValueError("synthetic PDF must contain at least one page")

    unicode_codes: dict[str, int] = {}
    encoded_pages: list[tuple[list[bytes], int]] = []
    for page in pages:
        encoded_lines = [
            _encode_text(line, unicode_codes=unicode_codes)
            for line in page.lines
        ]
        encoded_pages.append((encoded_lines, page.rotation_degrees))

    page_object_ids = [5 + index * 2 for index in range(len(encoded_pages))]
    content_object_ids = [page_id + 1 for page_id in page_object_ids]

    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{object_id} 0 R" for object_id in page_object_ids)
    objects.append(
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_ids)} >>".encode("ascii")
    )
    objects.append(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
        b"/Encoding /WinAnsiEncoding /ToUnicode 4 0 R >>"
    )
    cmap = _cmap_bytes(unicode_codes)
    objects.append(
        b"<< /Length " + str(len(cmap)).encode("ascii") + b" >>\nstream\n"
        + cmap
        + b"endstream"
    )

    for (encoded_lines, rotation), content_object_id in zip(
        encoded_pages,
        content_object_ids,
        strict=True,
    ):
        rotation_clause = f" /Rotate {rotation}" if rotation else ""
        objects.append(
            (
                "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
                f"{rotation_clause} /Resources << /Font << /F1 3 0 R >> >> "
                f"/Contents {content_object_id} 0 R >>"
            ).encode("ascii")
        )

        commands = [b"BT", b"/F1 12 Tf", b"72 720 Td"]
        for line_index, encoded_line in enumerate(encoded_lines):
            if line_index:
                commands.append(b"0 -18 Td")
            commands.append(b"<" + encoded_line.hex().upper().encode("ascii") + b"> Tj")
        commands.append(b"ET")
        stream = b"\n".join(commands)
        objects.append(
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )

    payload = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_id, body in enumerate(objects, start=1):
        offsets.append(len(payload))
        payload.extend(f"{object_id} 0 obj\n".encode("ascii"))
        payload.extend(body)
        payload.extend(b"\nendobj\n")

    xref_offset = len(payload)
    payload.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    payload.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        payload.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    payload.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )

    output = Path(path)
    output.write_bytes(payload)
    return output
