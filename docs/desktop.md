# Desktop App

## Run From Source

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Run-Desktop.ps1
```

Equivalent direct command:

```powershell
.\.venv\Scripts\python.exe -m localdoc
```

## Build Windows Package

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Build-DesktopExe.ps1
```

The build creates:

```text
dist\LocalDoc\LocalDoc.exe
dist\LocalDoc-Windows.zip
dist\LocalDoc.exe.sha256
```

## Main Functions

- Add documents through file picker or drag-and-drop.
- Process a queue without blocking the interface.
- Convert documents to Markdown with MarkItDown.
- Convert images to Markdown with local Tesseract OCR.
- Preview generated Markdown.
- Copy Markdown to clipboard.
- Open the generated file or containing folder.
- Persist settings and conversion history locally.

## OCR

LocalDoc checks the configured Tesseract executable before reporting OCR as available. The common Windows path is:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Recommended language setting:

```text
spa+eng
```
