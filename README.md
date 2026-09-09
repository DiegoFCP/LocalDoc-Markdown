# LocalDoc Markdown

[![CI](https://github.com/DiegoFCP/LocalDoc-Markdown/actions/workflows/ci.yml/badge.svg)](https://github.com/DiegoFCP/LocalDoc-Markdown/actions/workflows/ci.yml)

LocalDoc Markdown is a Windows-friendly workstation app for converting local documents to Markdown. It wraps [Microsoft MarkItDown](https://github.com/microsoft/markitdown), adds a desktop UI, a Streamlit UI, a folder pipeline, and optional local OCR for images through Tesseract.

## Features

- Desktop app for non-technical users.
- Streamlit app for browser-based local use.
- PowerShell CLI wrapper for one-off conversions.
- Folder pipeline with SHA256 manifest to skip unchanged files.
- OCR for images with Tesseract (`spa+eng` by default).
- PyInstaller build script for a standalone Windows EXE.
- GitHub Actions CI and release workflow.

## Supported Inputs

MarkItDown handles common document formats such as:

- PDF
- Word (`.docx`, `.doc`)
- PowerPoint (`.pptx`)
- Excel (`.xlsx`, `.xls`)
- HTML, TXT, CSV, JSON, XML
- ZIP, EPUB, Outlook messages
- Audio files supported by MarkItDown dependencies

The desktop app also supports OCR for:

- JPG, JPEG, JFIF
- PNG
- BMP
- TIF, TIFF
- WebP

## Quick Start

### Option 1: Download the Desktop App

Download `MarkItDownDesktop.exe` from the [latest GitHub Release](https://github.com/DiegoFCP/LocalDoc-Markdown/releases/latest).

For image OCR, install Tesseract OCR separately. The app will auto-detect:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Option 2: Run from Source

```powershell
git clone https://github.com/DiegoFCP/LocalDoc-Markdown.git
cd LocalDoc-Markdown
powershell -ExecutionPolicy Bypass -File .\scripts\Setup-Environment.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\Run-Desktop.ps1
```

Validate the environment:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Check-Environment.ps1
```

## Streamlit UI

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Run-Streamlit.ps1
```

Open:

```text
http://127.0.0.1:8501
```

## CLI Conversion

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Convert-ToMarkdown.ps1 "C:\path\document.pdf"
```

Optionally pass an output path:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Convert-ToMarkdown.ps1 "C:\path\document.pdf" "C:\path\document.md"
```

## Folder Pipeline

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Process-MarkitdownInbox.ps1
```

Default folders:

```text
work\pipeline\input
work\pipeline\output
work\pipeline\logs
```

## Documentation

- [Installation](docs/installation.md)
- [User guide](docs/user-guide.md)
- [Desktop app](docs/desktop.md)
- [Streamlit app](docs/streamlit.md)
- [Folder pipeline](docs/pipeline.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Release process](docs/release.md)

## Build the Windows EXE

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Build-DesktopExe.ps1
```

Output:

```text
dist\MarkItDownDesktop.exe
```

## Project Layout

```text
apps/desktop/       Tkinter desktop app
apps/streamlit/     Streamlit app
scripts/            Setup, run, conversion, pipeline, and build scripts
docs/               User and maintainer documentation
examples/           Sample input and output
.github/workflows/  CI and release automation
```

## Notes

- The repository does not commit `.venv`, `work`, `dist`, or generated EXEs.
- Tesseract OCR is required only for image OCR.
- On Windows, use `scripts\Install-Tesseract-Windows.ps1` as a helper, or install Tesseract manually.
- `ffmpeg` may be required by MarkItDown for some audio/video workflows.
- The YouTube extra is intentionally not installed because it can be incompatible with Python 3.14.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

Third-party dependencies retain their own licenses. See [NOTICE.md](NOTICE.md).
