# LocalDoc 0.2 Architecture

LocalDoc 0.2 is being rebuilt as a Windows desktop-only application. The goal is to keep document processing local, isolate product logic from UI code, and make conversion state auditable per file.

## Layers

```text
UI
Application services
Domain
Infrastructure
Workers
```

The UI layer must not call MarkItDown, Tesseract, SQLite, or complex filesystem logic directly. It should interact with application services such as `ConversionManager`, `ConversionService`, `HistoryService`, and `SettingsService`.

## Package Layout

```text
src/localdoc/
  app.py
  __main__.py
  domain/
  application/
  infrastructure/
  workers/
```

## Domain

The central entity is `ConversionJob`. It owns file metadata, state, timestamps, strategy, output path, errors, attempts, and whether OCR is required.

Supported job states:

- `QUEUED`
- `PROCESSING`
- `COMPLETED`
- `FAILED`
- `CANCELLED`

The domain enforces valid state transitions and initial file validation.

## Infrastructure

Application data uses standard Windows user locations:

```text
%LOCALAPPDATA%\LocalDoc\
```

Default Markdown output uses:

```text
%USERPROFILE%\Documents\LocalDoc\Markdown
```

SQLite stores conversion history metadata. Logs use local rotating files and must not store document content.

## Adapters

MarkItDown and Tesseract are wrapped behind adapters. This keeps UI and application services independent from third-party APIs and preserves a path for future replacement or extension.

## Current Phase

Phase 2 adds the conversion engine foundation:

- `ConversionManager` can add files, process one job, process a batch, cancel pending jobs, request active cancellation, retry failed jobs, and clear finished jobs.
- `ProcessConversionRunner` executes one conversion at a time in a spawned process and enforces a per-file timeout.
- `ConversionService` remains available for direct service tests and non-process adapters.
- The process runner creates MarkItDown and Tesseract adapters inside the child process so the UI layer does not depend on those third-party APIs.

The final PySide6 UI, polished worker progress signals, packaging changes, and desktop-only documentation rewrite are intentionally left for later phases.
