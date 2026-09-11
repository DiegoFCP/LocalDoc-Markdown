# Contributing

Thanks for considering a contribution.

## Local Setup

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Setup-Environment.ps1
```

## Validate Changes

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q src tests packaging
```

## Pull Requests

- Keep changes focused.
- Do not commit `.venv`, `work`, `dist`, generated EXEs, or local documents.
- Update docs when changing user-facing behavior.
- Mention whether the change affects conversion behavior, OCR, desktop UI, packaging, or documentation.
