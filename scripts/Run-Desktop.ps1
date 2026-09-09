$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$App = Join-Path $RepoRoot "apps\desktop\app.py"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "No existe .venv. Ejecuta scripts\Setup-Environment.ps1 primero."
}

& $Python $App
