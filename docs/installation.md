# Installation

## Option 1: Download the Desktop App

Download `MarkItDownDesktop.exe` from the latest GitHub Release.

The EXE includes the Python app and Python dependencies. For image OCR, install Tesseract OCR separately.

## Option 2: Run from Source

```powershell
git clone https://github.com/DiegoFCP/LocalDoc-Markdown.git
cd LocalDoc-Markdown
powershell -ExecutionPolicy Bypass -File .\scripts\Setup-Environment.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\Run-Desktop.ps1
```

## Tesseract OCR

Install Tesseract OCR if you want image-to-Markdown conversion.

Helper script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Install-Tesseract-Windows.ps1
```

Expected Windows path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Recommended languages:

```text
spa
eng
```

Validate:

```powershell
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
```
