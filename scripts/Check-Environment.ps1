$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$MarkItDown = Join-Path $RepoRoot ".venv\Scripts\markitdown.exe"
$Tesseract = "C:\Program Files\Tesseract-OCR\tesseract.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "No existe .venv. Ejecuta scripts\Setup-Environment.ps1 primero."
}

Write-Host "Python"
& $Python --version

Write-Host "`nPython packages"
& $Python -m pip show markitdown
& $Python -m pip show streamlit
& $Python -m pip show pytesseract
& $Python -m pip show pillow
& $Python -m pip show pyinstaller

Write-Host "`nImports"
& $Python -c "import markitdown, streamlit, pytesseract; from PIL import Image; print('imports ok')"

Write-Host "`nMarkItDown"
& $MarkItDown --version

Write-Host "`nDependency check"
& $Python -m pip check

Write-Host "`nTesseract"
if (Test-Path -LiteralPath $Tesseract) {
    & $Tesseract --version
    & $Tesseract --list-langs
} else {
    Write-Host "Tesseract no encontrado en $Tesseract"
}
