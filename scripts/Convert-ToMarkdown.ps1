param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$InputPath,

    [Parameter(Mandatory = $false, Position = 1)]
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

$WorkspaceRoot = Split-Path -Parent $PSScriptRoot
$MarkItDown = Join-Path $WorkspaceRoot ".venv\Scripts\markitdown.exe"

if (-not (Test-Path -LiteralPath $MarkItDown)) {
    throw "No se encontro MarkItDown en $MarkItDown. Reinstala el entorno o revisa la ruta."
}

if (-not (Test-Path -LiteralPath $InputPath)) {
    throw "No se encontro el archivo de entrada: $InputPath"
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $directory = Split-Path -Parent $InputPath
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($InputPath)
    $OutputPath = Join-Path $directory "$baseName.md"
}

& $MarkItDown $InputPath -o $OutputPath
if ($LASTEXITCODE -ne 0) {
    throw "markitdown finalizo con codigo $LASTEXITCODE"
}

Write-Host "Markdown generado en: $OutputPath"
