# Installation

## Option 1: Download The Desktop App

Download `LocalDoc-Windows.zip` from the latest GitHub Release.

1. Extract the ZIP.
2. Run `LocalDoc\LocalDoc.exe`.
3. Install Tesseract OCR separately if you need image OCR.

## Option 2: Run From Source

Requirements:

- Windows 10 or newer.
- Python 3.12 for release parity.
- Git.

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

Validate:

```powershell
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
```
