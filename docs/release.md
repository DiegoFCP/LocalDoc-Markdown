# Release Process

Releases are built by GitHub Actions when a version tag is pushed.

## Before Tagging

Run locally:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,build]"
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q src tests
powershell -ExecutionPolicy Bypass -File .\scripts\Build-DesktopExe.ps1
```

## Create A Release

```powershell
git tag v0.2.0
git push origin v0.2.0
```

The release workflow builds and uploads:

```text
LocalDoc-Windows.zip
LocalDoc.exe.sha256
```

Users extract the ZIP and run:

```text
LocalDoc\LocalDoc.exe
```
