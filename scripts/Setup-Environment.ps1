$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = "python"
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

Set-Location $RepoRoot

if (-not (Test-Path -LiteralPath $VenvPython)) {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        throw "python -m venv finalizo con codigo $LASTEXITCODE"
    }
}

& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "pip install --upgrade pip finalizo con codigo $LASTEXITCODE"
}

& $VenvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "pip install -r requirements.txt finalizo con codigo $LASTEXITCODE"
}

Write-Host "Entorno listo en $RepoRoot\.venv"
