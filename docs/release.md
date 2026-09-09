# Release Process

Releases are built by GitHub Actions when a version tag is pushed.

## Create a Release

```powershell
git tag v0.1.0
git push origin v0.1.0
```

The release workflow builds:

```text
dist\MarkItDownDesktop.exe
```

Then it uploads the EXE to the GitHub Release.

## Local Build

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Build-DesktopExe.ps1
```
