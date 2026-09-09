$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$Tesseract = "C:\Program Files\Tesseract-OCR\tesseract.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "No existe .venv. Ejecuta scripts\Setup-Environment.ps1 primero."
}

Write-Host "Python"
& $Python --version

Write-Host "`nPython packages"
& $Python -m pip show markitdown
& $Python -m pip show PySide6
& $Python -m pip show pytesseract
& $Python -m pip show pillow
& $Python -m pip show pyinstaller

Write-Host "`nImports"
& $Python -c "import markitdown, pytesseract; from PIL import Image; from PySide6.QtWidgets import QApplication; print('imports ok')"

Write-Host "`nDependency check"
& $Python -m pip check

Write-Host "`nTesseract"
if (Test-Path -LiteralPath $Tesseract) {
    & $Tesseract --version
    & $Tesseract --list-langs
} else {
    Write-Host "Tesseract no encontrado en $Tesseract"
}
