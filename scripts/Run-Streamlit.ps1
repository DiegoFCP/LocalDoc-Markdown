$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$App = Join-Path $RepoRoot "apps\streamlit\app.py"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "No existe .venv. Ejecuta scripts\Setup-Environment.ps1 primero."
}

& $Python -m streamlit run $App --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
