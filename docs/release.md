# Release Process

Releases are built by GitHub Actions when a version tag is pushed.

## Create a Release

```powershell
git tag v0.1.2
git push origin v0.1.2
```

The release workflow builds:

```text
dist\MarkItDownDesktop.exe
dist\MarkItDownDesktop.exe.sha256
```

Then it uploads the EXE and checksum to the GitHub Release.

## Before Tagging

Run:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
powershell -ExecutionPolicy Bypass -File .\scripts\Check-Environment.ps1
```

## Local Build

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Build-DesktopExe.ps1
```

The script uses `.venv\Scripts\python.exe` when it exists. In CI it falls back to the runner Python.
