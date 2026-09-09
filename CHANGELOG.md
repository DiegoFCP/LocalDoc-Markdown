# Changelog

## 0.2.0

- Started the Desktop-only rebuild foundation.
- Added `src/localdoc` architecture with domain, application, infrastructure, and worker layers.
- Added `ConversionJob`, job states, conversion strategy, settings, file limits, and state transition rules.
- Added SQLite-backed conversion history repository.
- Added settings persistence using `%LOCALAPPDATA%\LocalDoc`.
- Added MarkItDown and Tesseract adapters.
- Added local rotating logging setup.
- Added unit tests for domain, settings, filesystem, SQLite persistence, and conversion manager behavior.
- Updated runtime dependency direction for LocalDoc 0.2: PySide6, MarkItDown 0.1.7, Tesseract OCR, and Desktop-only extras.

## 0.1.2

- Added shared `localdoc_markdown` core utilities for safe filenames, hashes, manifests, supported formats, and processing limits.
- Added Pytest coverage for core safety behavior.
- Added Ruff linting and Pytest execution to CI.
- Added Dependabot and CodeQL workflows.
- Added checksum generation for release EXE artifacts.
- Hardened PowerShell scripts with native exit-code checks and safer CSV output.

## 0.1.0

- Initial public version.
- Desktop Tkinter app for converting local files to Markdown.
- Optional local OCR for images through Tesseract and pytesseract.
- Streamlit interface for local browser-based conversion.
- PowerShell scripts for setup, CLI conversion, folder pipeline, and EXE packaging.
- GitHub Actions CI and release build workflow.
