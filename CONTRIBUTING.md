# Contributing

Thanks for considering a contribution.

## Local Setup

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Setup-Environment.ps1
```

## Validate Changes

```powershell
.\.venv\Scripts\python.exe -m py_compile apps\desktop\app.py apps\streamlit\app.py
.\.venv\Scripts\python.exe -m pip check
powershell -ExecutionPolicy Bypass -File .\scripts\Check-Environment.ps1
```

## Pull Requests

- Keep changes focused.
- Do not commit `.venv`, `work`, `dist`, generated EXEs, or local documents.
- Update docs when changing user-facing behavior.
- Mention whether the change affects desktop, Streamlit, CLI, pipeline, or packaging.
