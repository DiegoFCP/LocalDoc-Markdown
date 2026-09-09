$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$App = Join-Path $RepoRoot "apps\desktop\app.py"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "No existe .venv. Ejecuta scripts\Setup-Environment.ps1 primero."
}

Set-Location $RepoRoot

& $Python -m pip install "pyinstaller>=6.20.0"
& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onefile `
    --name MarkItDownDesktop `
    --distpath dist `
    --workpath work\pyinstaller-build `
    --specpath work\pyinstaller-spec `
    --collect-all magika `
    --collect-all markitdown `
    --collect-all pytesseract `
    --collect-all PIL `
    $App

Write-Host "EXE generado en: $RepoRoot\dist\MarkItDownDesktop.exe"
