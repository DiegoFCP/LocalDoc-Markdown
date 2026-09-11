# Quickstart

## Install Dependencies

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Setup-Environment.ps1
```

## Run The Desktop App

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Run-Desktop.ps1
```

## Convert A File

1. Drop a file into LocalDoc, or use `Seleccionar archivos`.
2. Start the conversion.
3. Select the completed row to preview or open the Markdown output.

## Verify The Environment

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Check-Environment.ps1
```

## Build The Windows Package

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Build-DesktopExe.ps1
```
