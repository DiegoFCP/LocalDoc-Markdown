# LocalDoc Markdown

[![CI](https://github.com/DiegoFCP/LocalDoc-Markdown/actions/workflows/ci.yml/badge.svg)](https://github.com/DiegoFCP/LocalDoc-Markdown/actions/workflows/ci.yml)

LocalDoc Markdown is a private Windows desktop app for converting local documents to Markdown. It wraps [Microsoft MarkItDown](https://github.com/microsoft/markitdown), adds a PySide6 interface, keeps a local SQLite history, and supports optional image OCR through local Tesseract.

No document content is sent to cloud services by LocalDoc.

## Features

- Desktop-only Windows app built with PySide6.
- Batch queue with per-file states.
- Drag-and-drop or file picker input.
- Markdown preview for completed conversions.
- Local SQLite conversion history.
- Optional Tesseract OCR for images.
- Process-isolated conversions with per-file timeout.
- PyInstaller Windows release workflow with SHA256 checksum.

## Supported Inputs

The initial 0.2.0 surface supports the formats covered by current tests and adapters:

- TXT
- HTML
- PDF
- Word `.docx`
- PowerPoint `.pptx`
- Excel `.xlsx`
- CSV, JSON, XML
- Images for OCR: PNG, JPG/JPEG, BMP, TIFF, WebP

MarkItDown may support more formats internally, but LocalDoc only documents formats validated for this desktop release.

## Download

Download `LocalDoc-Windows.zip` from the [latest GitHub Release](https://github.com/DiegoFCP/LocalDoc-Markdown/releases/latest), extract it, and run:

```text
LocalDoc\LocalDoc.exe
```

For image OCR, install Tesseract OCR separately. The default Windows path is:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Run From Source

```powershell
git clone https://github.com/DiegoFCP/LocalDoc-Markdown.git
cd LocalDoc-Markdown
powershell -ExecutionPolicy Bypass -File .\scripts\Setup-Environment.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\Run-Desktop.ps1
```

## Quality Checks

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q src tests
```

## Build

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Build-DesktopExe.ps1
```

Outputs:

```text
dist\LocalDoc\LocalDoc.exe
dist\LocalDoc-Windows.zip
dist\LocalDoc.exe.sha256
```

## Project Layout

```text
src/localdoc/          Desktop application source
tests/                 Unit, integration, and UI smoke tests
scripts/               Development, validation, OCR install, and build helpers
packaging/             PyInstaller spec
docs/                  User and maintainer documentation
examples/              Small sample input and output
.github/workflows/     CI and release automation
```

## Documentation

- [Installation](docs/installation.md)
- [User guide](docs/user-guide.md)
- [Desktop app](docs/desktop.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Release process](docs/release.md)
- [Architecture](docs/architecture.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

Third-party dependencies retain their own licenses. See [NOTICE.md](NOTICE.md).
