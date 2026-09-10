from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import re
import warnings
import zipfile
import xml.etree.ElementTree as ET
from typing import Iterable


@dataclass(frozen=True)
class LeakFinding:
    kind: str
    location: str
    evidence: str


@dataclass
class LeakReport:
    findings: list[LeakFinding] = field(default_factory=list)
    requires_manual_visual_review: bool = False

    @property
    def automated_checks_passed(self) -> bool:
        return not self.findings

    @property
    def passed(self) -> bool:
        """Fail closed: visual derivatives are not publishable before manual review."""
        return not self.findings and not self.requires_manual_visual_review


# Deliberately conservative for public fixtures. False positives should force
# review rather than allow a private identifier through.
_BLOCKING_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("email", re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")),
    ("url", re.compile(r"(?i)\b(?:https?://|www\.)\S+")),
    ("inn", re.compile(r"(?i)\bИНН\s*[:№]?\s*\d{10,12}\b")),
    ("kpp", re.compile(r"(?i)\bКПП\s*[:№]?\s*\d{9}\b")),
    ("ogrn", re.compile(r"(?i)\bОГРН(?:ИП)?\s*[:№]?\s*\d{13,15}\b")),
    ("bik", re.compile(r"(?i)\bБИК\s*[:№]?\s*\d{9}\b")),
    ("bank_account", re.compile(r"(?<!\d)\d{20}(?!\d)")),
    ("phone", re.compile(r"(?<!\d)(?:\+7|8)[\s()\-]*\d{3}[\s()\-]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}(?!\d)")),
)

_XLSX_FORBIDDEN_MEMBER_MARKERS = (
    "xl/externallinks/",
    "xl/comments",
    "xl/threadedcomments/",
    "xl/persons/",
    "xl/embeddings/",
    "xl/oleobjects/",
    "xl/vbaproject.bin",
    "customxml/",
    "docprops/custom.xml",
)


def scan_text(
    text: str,
    *,
    location: str = "text",
    forbidden_tokens: Iterable[str] = (),
    include_url: bool = True,
) -> list[LeakFinding]:
    findings: list[LeakFinding] = []
    for kind, pattern in _BLOCKING_PATTERNS:
        if kind == "url" and not include_url:
            continue
        if pattern.search(text):
            findings.append(LeakFinding(kind, location, f"matched {kind} pattern"))

    folded = text.casefold()
    for token in forbidden_tokens:
        normalized = token.strip()
        if normalized and normalized.casefold() in folded:
            findings.append(LeakFinding("forbidden_token", location, "matched local denylist token"))
    return findings


def _scan_json(path: Path, forbidden_tokens: Iterable[str]) -> LeakReport:
    report = LeakReport()
    raw = path.read_text(encoding="utf-8")
    report.findings.extend(scan_text(raw, location="json-content", forbidden_tokens=forbidden_tokens))
    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        report.findings.append(LeakFinding("invalid_json", "json-structure", f"parse error at line {exc.lineno}"))
    return report


def _scan_xlsx(path: Path, forbidden_tokens: Iterable[str]) -> LeakReport:
    report = LeakReport()
    try:
        with zipfile.ZipFile(path) as archive:
            for index, name in enumerate(archive.namelist(), start=1):
                lower = name.lower()
                location = f"xlsx-member-{index}"
                if any(marker in lower for marker in _XLSX_FORBIDDEN_MEMBER_MARKERS):
                    report.findings.append(
                        LeakFinding("forbidden_xlsx_part", location, "forbidden internal XLSX part")
                    )
                report.findings.extend(scan_text(name, location=location, forbidden_tokens=forbidden_tokens))
                if lower.endswith((".xml", ".rels")):
                    data = archive.read(name)
                    try:
                        root = ET.fromstring(data)
                    except ET.ParseError:
                        report.findings.append(LeakFinding("invalid_xlsx_xml", location, "unparseable XML part"))
                        continue
                    for elem in root.iter():
                        if elem.text:
                            report.findings.extend(
                                scan_text(elem.text, location=location, forbidden_tokens=forbidden_tokens)
                            )
                        if elem.tail:
                            report.findings.extend(
                                scan_text(elem.tail, location=location, forbidden_tokens=forbidden_tokens)
                            )
                        attrs = {k.rsplit("}", 1)[-1]: str(v) for k, v in elem.attrib.items()}
                        if attrs.get("TargetMode", "").casefold() == "external":
                            report.findings.append(
                                LeakFinding("external_relationship", location, "external relationship present")
                            )
                            report.findings.extend(
                                scan_text(
                                    attrs.get("Target", ""),
                                    location=location,
                                    forbidden_tokens=forbidden_tokens,
                                )
                            )
                        for attr_name, attr_value in attrs.items():
                            if attr_name in {"Type", "Target", "TargetMode"}:
                                continue
                            report.findings.extend(
                                scan_text(
                                    attr_value,
                                    location=location,
                                    forbidden_tokens=forbidden_tokens,
                                    include_url=False,
                                )
                            )
                elif lower.endswith(".txt"):
                    text = archive.read(name).decode("utf-8", errors="ignore")
                    report.findings.extend(scan_text(text, location=location, forbidden_tokens=forbidden_tokens))
    except zipfile.BadZipFile:
        report.findings.append(LeakFinding("invalid_xlsx", "xlsx-container", "not a valid XLSX/ZIP container"))
    return report


def _scan_image(path: Path, forbidden_tokens: Iterable[str]) -> LeakReport:
    from PIL import Image

    report = LeakReport(requires_manual_visual_review=True)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as image:
                if getattr(image, "n_frames", 1) != 1:
                    report.findings.append(
                        LeakFinding("image_multiframe", "image-container", "visual derivative must contain one frame")
                    )
                exif = image.getexif()
                if exif and len(exif):
                    report.findings.append(
                        LeakFinding("image_exif_present", "image-metadata", "EXIF metadata present")
                    )
                    for value in exif.values():
                        if isinstance(value, str):
                            report.findings.extend(
                                scan_text(value, location="image-metadata", forbidden_tokens=forbidden_tokens)
                            )
                # Stage 1P visual derivatives are intended to be pixel-only.
                # Any auxiliary image info (including ICC/XMP/text chunks) is blocking.
                for value in image.info.values():
                    if value not in (None, "", b""):
                        report.findings.append(
                            LeakFinding("image_metadata_present", "image-metadata", "auxiliary image metadata present")
                        )
                        if isinstance(value, str):
                            report.findings.extend(
                                scan_text(value, location="image-metadata", forbidden_tokens=forbidden_tokens)
                            )
                        elif isinstance(value, bytes):
                            decoded = value.decode("utf-8", errors="ignore")
                            if decoded:
                                report.findings.extend(
                                    scan_text(decoded, location="image-metadata", forbidden_tokens=forbidden_tokens)
                                )
    except (Image.DecompressionBombWarning, Image.DecompressionBombError):
        report.findings.append(
            LeakFinding("image_resource_limit", "image-container", "image exceeds safe decode limits")
        )
    return report


def scan_path(path: str | Path, *, forbidden_tokens: Iterable[str]) -> LeakReport:
    p = Path(path)
    filename_findings = scan_text(p.name, location="filename", forbidden_tokens=forbidden_tokens)
    suffix = p.suffix.lower()
    if suffix == ".json":
        report = _scan_json(p, forbidden_tokens)
    elif suffix == ".xlsx":
        report = _scan_xlsx(p, forbidden_tokens)
    elif suffix in {".png", ".jpg", ".jpeg"}:
        report = _scan_image(p, forbidden_tokens)
    else:
        report = LeakReport()
        report.findings.append(
            LeakFinding("unsupported_format", "file", f"unsupported public derivative format: {suffix}")
        )

    report.findings[:0] = filename_findings
    return report
