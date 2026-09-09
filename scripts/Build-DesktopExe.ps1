param(
    [string]$PythonExe = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$App = Join-Path $RepoRoot "apps\desktop\app.py"

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
Invoke-NativeCommand -FilePath $PythonExe -Arguments @(
    "-m",
    "PyInstaller",
    "--noconfirm",
    "--clean",
    "--windowed",
    "--onefile",
    "--name",
    "MarkItDownDesktop",
    "--distpath",
    "dist",
    "--workpath",
    "work\pyinstaller-build",
    "--specpath",
    "work\pyinstaller-spec",
    "--collect-all",
    "magika",
    "--collect-all",
    "markitdown",
    "--collect-all",
    "pytesseract",
    "--collect-all",
    "PIL",
    $App
)

Write-Host "EXE generado en: $RepoRoot\dist\MarkItDownDesktop.exe"
