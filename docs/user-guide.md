# User Guide

## Convert Documents

1. Open LocalDoc.
2. Drop files into the input area, or use `Seleccionar archivos`.
3. Confirm the output folder in settings if needed.
4. Start the conversion.
5. Select a completed row to preview, copy, or open the Markdown output.

Markdown files are written to the configured output folder. By default, LocalDoc uses:

```text
%USERPROFILE%\Documents\LocalDoc\Markdown
```

Local technical data such as settings, logs, and SQLite history is stored under:

```text
%LOCALAPPDATA%\LocalDoc
```

## OCR For Images

LocalDoc uses Tesseract only for image files.

1. Install Tesseract OCR.
2. Open settings.
3. Enable OCR.
4. Confirm the `tesseract.exe` path.
5. Use `spa+eng`, or any language code installed in Tesseract.

If a language is missing, install its Tesseract language data and try again.

## Limits

The first desktop release applies conservative limits:

- Up to 100 files per queue.
- Up to 100 MB per file.
- Per-file timeout from settings.

Files over those limits are rejected before conversion.
