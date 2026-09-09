param(
    [string]$PythonExe = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$SpecFile = Join-Path $RepoRoot "packaging\LocalDoc.spec"

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$FilePath finalizo con codigo $LASTEXITCODE"
    }
}

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    if (Test-Path -LiteralPath $VenvPython) {
        $PythonExe = $VenvPython
    }
    else {
        $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if ($null -eq $PythonCommand) {
            throw "No se encontro Python. Ejecuta scripts\Setup-Environment.ps1 localmente o instala Python en el runner."
        }

        $PythonExe = $PythonCommand.Source
    }
}

Set-Location $RepoRoot

Write-Host "Usando Python: $PythonExe"

Invoke-NativeCommand -FilePath $PythonExe -Arguments @("-m", "pip", "install", "pyinstaller>=6.20.0")
Invoke-NativeCommand -FilePath $PythonExe -Arguments @("-m", "pip", "install", "-e", ".[build]")
Invoke-NativeCommand -FilePath $PythonExe -Arguments @(
    "-m",
    "PyInstaller",
    "--clean",
    "--noconfirm",
    $SpecFile
)

$ExePath = Join-Path $RepoRoot "dist\LocalDoc\LocalDoc.exe"
if (-not (Test-Path -LiteralPath $ExePath)) {
    throw "No se genero $ExePath"
}

$ChecksumPath = Join-Path $RepoRoot "dist\LocalDoc.exe.sha256"
Get-FileHash -LiteralPath $ExePath -Algorithm SHA256 |
    ForEach-Object { "$($_.Hash)  LocalDoc.exe" } |
    Set-Content -LiteralPath $ChecksumPath -Encoding ascii

$ZipPath = Join-Path $RepoRoot "dist\LocalDoc-Windows.zip"
if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}
Compress-Archive -LiteralPath (Join-Path $RepoRoot "dist\LocalDoc") -DestinationPath $ZipPath -Force

Write-Host "EXE generado en: $ExePath"
Write-Host "Checksum generado en: $ChecksumPath"
Write-Host "Paquete portable generado en: $ZipPath"
