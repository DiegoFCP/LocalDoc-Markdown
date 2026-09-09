# Pipeline por carpetas

El pipeline convierte documentos de una carpeta de entrada a Markdown, preserva subcarpetas y mantiene un manifest con hash SHA256 para evitar reconvertir archivos sin cambios.

## Ejecutar

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Process-MarkitdownInbox.ps1
```

## Carpetas por defecto

```text
work\pipeline\input
work\pipeline\output
work\pipeline\logs
```

## Usar carpetas propias

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Process-MarkitdownInbox.ps1 `
  -InputDir "D:\Documentos\entrada" `
  -OutputDir "D:\Documentos\markdown" `
  -LogDir "D:\Documentos\logs"
```

## Forzar reconversion

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Process-MarkitdownInbox.ps1 -Force
```

## Programar con Windows Task Scheduler

```powershell
$RepoRoot = "C:\Users\SistemaNeumachile\Documents\Proyectos\Python\Markitdown"
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$RepoRoot\scripts\Process-MarkitdownInbox.ps1`""
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName "MarkItDown Pipeline" -Action $Action -Trigger $Trigger -Description "Convierte documentos a Markdown con MarkItDown"
```

El OCR de imagenes vive en la app de escritorio, donde se configura Tesseract.
