# Stage 1P Dependency & License Manifest

Date checked: 2026-09-10

Scope: executable dependencies introduced by PR #2 for the bounded Stage 1P anonymization prototype. This is not a general production lockfile for future Stroy-Snab stages.

## Runtime dependencies

| Package | Tested version | Stage 1P role | License | Distribution note |
|---|---:|---|---|---|
| XlsxWriter | 3.2.9 | build new sanitized XLSX containers | BSD-2-Clause | permissive; do not copy private source workbook internals |
| Pillow | 12.3.0 | image decode/re-encode and pixel redaction | MIT-CMU | permissive |
| pypdfium2 | 5.13.0 | PDFium page rendering into new PNG derivatives | Apache-2.0 OR BSD-3-Clause for wrapper; PDFium BSD-style plus third-party dependency licenses | any future binary redistribution must retain the PDFium/dependency license material shipped with the pypdfium2/PDFium build used |

`pyproject.toml` currently constrains compatible major/minor ranges rather than pinning one exact installation. The versions above are the exact versions exercised by the acceptance-candidate hosted CI. A dependency upgrade is not accepted merely because it satisfies the range: material version changes must be re-tested and recorded in evidence before a later packaged release relies on them.

## Test/readback dependencies

| Package | Tested version | Role | License |
|---|---:|---|---|
| openpyxl | 3.1.5 | XLSX readback/inspection in tests and bounded private experiment | MIT/Expat |
| pytest | 9.1.1 | test runner | MIT |
| et-xmlfile | 2.0.0 | transitive dependency of openpyxl in tested environment | MIT |

Other pytest support packages installed transitively by the hosted runner are development-only and are not imported by the Stage 1P runtime package.

## Evidence source

Hosted CI installs and reports the concrete package versions before compiling/running tests. The pre-freeze synchronized head `69a63f91d89d5efb14b539496567c0ffe1f545ff` used:

- XlsxWriter 3.2.9;
- Pillow 12.3.0;
- pypdfium2 5.13.0;
- openpyxl 3.1.5;
- pytest 9.1.1;
- et-xmlfile 2.0.0.

The final candidate HEAD must independently pass the same hosted CI matrix after this manifest is added.

## Upstream license references checked

- XlsxWriter: https://pypi.org/project/XlsxWriter/
- Pillow: https://pypi.org/project/pillow/
- pypdfium2 5.13.0: https://pypi.org/project/pypdfium2/5.13.0/
- openpyxl: https://pypi.org/project/openpyxl/
- pytest: https://pypi.org/project/pytest/
- et-xmlfile: https://pypi.org/project/et-xmlfile/

The pypdfium2 upstream explicitly states that PDFium and dependency licenses must accompany binary redistributions. Stage 1P currently commits source code and a small XLSX fixture only; it does not commit or redistribute a PDFium binary. A future installer/executable packaging step must copy the applicable license bundle from the exact pypdfium2/PDFium artifact rather than reconstructing that notice from this summary.

## Adoption boundary

This manifest closes the Stage 1P source-prototype dependency/license inventory requirement only. It does not grant automatic production adoption to later versions, OCR/VLM packages, Docling, PaddleOCR, ERP components, CAP integrations or any future packaged executable.
