# Changelog

## 0.2.0

- Started the Desktop-only rebuild foundation.
- Added `src/localdoc` architecture with domain, application, infrastructure, and worker layers.
- Added `ConversionJob`, job states, conversion strategy, settings, file limits, and state transition rules.
- Added SQLite-backed conversion history repository.
- Added settings persistence using `%LOCALAPPDATA%\LocalDoc`.
- Added MarkItDown and Tesseract adapters.
- Added local rotating logging setup.
- Added a process-isolated conversion runner with per-file timeout handling.
- Expanded `ConversionManager` with batch processing, pending cancellation, active cancellation request, retry, and clear-finished behavior.
- Added a PySide6 desktop shell with header, OCR status, drag-and-drop zone, queue table, contextual panel, Markdown preview, and settings dialog.
- Integrated the PySide6 shell with conversion manager, settings, SQLite history, MarkItDown process runner, and Tesseract status.
- Updated the internal desktop development launcher to run `python -m localdoc`.
- Added unit tests for domain, settings, filesystem, SQLite persistence, and conversion manager behavior.
- Added integration tests for process-based conversion and timeout behavior.
- Added UI smoke tests for LocalDoc main window, queue population, and preview rendering.
- Updated runtime dependency direction for LocalDoc 0.2: PySide6, MarkItDown 0.1.7, Tesseract OCR, and Desktop-only extras.
- Removed the legacy Tkinter app, Streamlit app, CLI conversion wrapper, folder pipeline, and old shared package from the product surface.
- Added hardening coverage for duplicate queue items, deleted queued files, queue limits, long Unicode names, output collisions, timeout handling, and missing OCR engine errors.
- Added a committed PyInstaller spec for the Windows `onedir` build and updated release automation to publish `LocalDoc-Windows.zip` plus SHA256 checksum.
- Added UX-1 design system foundations with reusable tokens, light/dark theme generation, focus states, and button components.
- Added UX-2 through UX-7 desktop redesign work: header navigation, converter view extraction, contextual preview/details panel, local history view, sectioned settings dialog, theme preference, and LocalDoc branding assets.

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
