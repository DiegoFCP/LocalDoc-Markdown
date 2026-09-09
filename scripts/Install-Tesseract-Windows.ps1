$ErrorActionPreference = "Stop"

$Tesseract = "C:\Program Files\Tesseract-OCR\tesseract.exe"

if (Test-Path -LiteralPath $Tesseract) {
    Write-Host "Tesseract ya esta instalado en $Tesseract"
    & $Tesseract --version
    exit 0
}

if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget install --id UB-Mannheim.TesseractOCR -e
    exit $LASTEXITCODE
}

if (Get-Command choco -ErrorAction SilentlyContinue) {
    choco install tesseract -y
    exit $LASTEXITCODE
}

throw "No encontre winget ni choco. Instala Tesseract OCR manualmente desde https://github.com/UB-Mannheim/tesseract/wiki"
