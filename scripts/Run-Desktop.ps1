$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "No existe .venv. Ejecuta scripts\Setup-Environment.ps1 primero."
}

Set-Location $RepoRoot
& $Python -m localdoc
if ($LASTEXITCODE -ne 0) {
    throw "LocalDoc finalizo con codigo $LASTEXITCODE"
}
