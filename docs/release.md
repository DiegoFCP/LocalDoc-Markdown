# Release Process

Releases are built by GitHub Actions when a version tag is pushed. The public artifact is a portable Windows ZIP; users do not need Python when they use the ZIP.

## Before Tagging

Start from a clean tree on the branch that will be released:

```powershell
git status --short --branch
git pull --ff-only
```

Run the local validation gate:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,build]"
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q src tests packaging
powershell -ExecutionPolicy Bypass -File .\scripts\Build-DesktopExe.ps1
```

Confirm these files exist locally:

```text
dist\LocalDoc\LocalDoc.exe
dist\LocalDoc-Windows.zip
dist\LocalDoc.exe.sha256
```

## Create A Release

Merge the release branch to `main`, then create and push a version tag:

```powershell
git checkout main
git pull --ff-only
git merge --no-ff codex/desktop-rebuild-v0.2
git push origin main
git tag v0.2.0
git push origin v0.2.0
```

The release workflow runs Ruff, compileall, pip check, Pytest, builds the Windows app, and uploads:

```text
LocalDoc-Windows.zip
LocalDoc.exe.sha256
```

Users extract the ZIP and run:

```text
LocalDoc\LocalDoc.exe
```

## Verify The Published Artifact

After GitHub Actions finishes, download the ZIP and checksum from the release page. From the extracted folder:

```powershell
Get-FileHash -LiteralPath .\LocalDoc\LocalDoc.exe -Algorithm SHA256
```

Compare the hash with `LocalDoc.exe.sha256`.

## Public Release Notes

Mention these points in the release description:

- LocalDoc runs locally and does not upload document content.
- Tesseract OCR is required separately for image OCR.
- The Windows package is portable; extract the ZIP before running `LocalDoc.exe`.
- The EXE is currently unsigned, so Windows SmartScreen may show a warning.
