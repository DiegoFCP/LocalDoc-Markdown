param(
    [Parameter(Mandatory = $false)]
    [string]$InputDir,

    [Parameter(Mandatory = $false)]
    [string]$OutputDir,

    [Parameter(Mandatory = $false)]
    [string]$LogDir,

    [Parameter(Mandatory = $false)]
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$WorkspaceRoot = Split-Path -Parent $PSScriptRoot
$MarkItDown = Join-Path $WorkspaceRoot ".venv\Scripts\markitdown.exe"

if ([string]::IsNullOrWhiteSpace($InputDir)) {
    $InputDir = Join-Path $WorkspaceRoot "work\pipeline\input"
}

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $WorkspaceRoot "work\pipeline\output"
}

if ([string]::IsNullOrWhiteSpace($LogDir)) {
    $LogDir = Join-Path $WorkspaceRoot "work\pipeline\logs"
}
$ManifestPath = Join-Path $LogDir "manifest.csv"
$RunLogPath = Join-Path $LogDir ("run-{0}.log" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
$SupportedExtensions = @(
    ".pdf", ".docx", ".doc", ".pptx", ".xlsx", ".xls",
    ".html", ".htm", ".txt", ".csv", ".json", ".xml", ".zip",
    ".epub", ".msg", ".wav", ".mp3"
)

function Write-RunLog {
    param([string]$Message)
    $line = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -LiteralPath $RunLogPath -Value $line
    Write-Host $line
}

function Get-FileSha256 {
    param([string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

function Get-RelativePathCompat {
    param(
        [string]$BasePath,
        [string]$TargetPath
    )

    $baseFullPath = [System.IO.Path]::GetFullPath($BasePath)
    $targetFullPath = [System.IO.Path]::GetFullPath($TargetPath)

    if (-not $baseFullPath.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
        $baseFullPath = $baseFullPath + [System.IO.Path]::DirectorySeparatorChar
    }

    $baseUri = New-Object System.Uri($baseFullPath)
    $targetUri = New-Object System.Uri($targetFullPath)
    $relativeUri = $baseUri.MakeRelativeUri($targetUri)
    return [System.Uri]::UnescapeDataString($relativeUri.ToString()).Replace("/", [System.IO.Path]::DirectorySeparatorChar)
}

New-Item -ItemType Directory -Force -Path $InputDir, $OutputDir, $LogDir | Out-Null

if (-not (Test-Path -LiteralPath $MarkItDown)) {
    throw "No se encontro MarkItDown en $MarkItDown"
}

if (-not (Test-Path -LiteralPath $ManifestPath)) {
    "source_path,source_hash,output_path,status,converted_at,error" | Set-Content -LiteralPath $ManifestPath
}

$previousRows = @{}
Import-Csv -LiteralPath $ManifestPath | ForEach-Object {
    if ($_.source_path -and $_.source_hash) {
        $previousRows[$_.source_path] = $_
    }
}

$newRows = New-Object System.Collections.Generic.List[object]
$files = Get-ChildItem -LiteralPath $InputDir -File -Recurse | Where-Object {
    $SupportedExtensions -contains $_.Extension.ToLowerInvariant()
}

Write-RunLog "Inicio pipeline. Archivos detectados: $($files.Count)"

foreach ($file in $files) {
    $sourcePath = $file.FullName
    $relativePath = Get-RelativePathCompat -BasePath $InputDir -TargetPath $sourcePath
    $relativeBase = [System.IO.Path]::ChangeExtension($relativePath, ".md")
    $outputPath = Join-Path $OutputDir $relativeBase
    $outputParent = Split-Path -Parent $outputPath
    New-Item -ItemType Directory -Force -Path $outputParent | Out-Null

    $hash = Get-FileSha256 -Path $sourcePath
    $existing = $previousRows[$sourcePath]

    if (-not $Force -and $existing -and $existing.source_hash -eq $hash -and (Test-Path -LiteralPath $outputPath)) {
        Write-RunLog "SKIP $relativePath"
        $newRows.Add([pscustomobject]@{
            source_path = $sourcePath
            source_hash = $hash
            output_path = $outputPath
            status = "skipped"
            converted_at = $existing.converted_at
            error = ""
        })
        continue
    }

    try {
        Write-RunLog "CONVERT $relativePath"
        & $MarkItDown $sourcePath -o $outputPath
        if ($LASTEXITCODE -ne 0) {
            throw "markitdown finalizo con codigo $LASTEXITCODE"
        }

        $newRows.Add([pscustomobject]@{
            source_path = $sourcePath
            source_hash = $hash
            output_path = $outputPath
            status = "converted"
            converted_at = (Get-Date).ToString("s")
            error = ""
        })
    }
    catch {
        Write-RunLog "ERROR $relativePath $($_.Exception.Message)"
        $newRows.Add([pscustomobject]@{
            source_path = $sourcePath
            source_hash = $hash
            output_path = $outputPath
            status = "error"
            converted_at = (Get-Date).ToString("s")
            error = $_.Exception.Message.Replace('"', "'")
        })
    }
}

$newRows | Export-Csv -LiteralPath $ManifestPath -NoTypeInformation
Write-RunLog "Fin pipeline. Manifest: $ManifestPath"
