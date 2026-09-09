# User Guide

## Desktop App

Run from source:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Run-Desktop.ps1
```

Or download `MarkItDownDesktop.exe` from Releases.

## Convert Documents

1. Click `Agregar archivos`.
2. Select one or more supported documents.
3. Choose an output folder.
4. Click `Convertir`.

Markdown files are written to the selected output folder.

The desktop and Streamlit apps apply default safety limits:

- Up to 100 files per batch.
- Up to 100 MB per file.

Files outside those limits are rejected before conversion with a visible message.

## Convert Images With OCR

1. Install Tesseract OCR.
2. Click `Detectar` in the OCR section.
3. Confirm the Tesseract path.
4. Keep language as `spa+eng` or change it.
5. Click `Agregar imagenes`.
6. Click `Convertir`.

## Pipeline Mode

Place files in:

```text
work\pipeline\input
```

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Process-MarkitdownInbox.ps1
```

Converted Markdown appears in:

```text
work\pipeline\output
```

Logs and manifest are written to:

```text
work\pipeline\logs
```

The CSV manifests protect text fields that start with `=`, `+`, `-`, or `@` so spreadsheet tools do not interpret them as formulas.
