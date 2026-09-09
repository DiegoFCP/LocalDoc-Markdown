# Quickstart

## Instalar dependencias

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Setup-Environment.ps1
```

## Convertir un archivo

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Convert-ToMarkdown.ps1 "C:\ruta\archivo.pdf"
```

Si no pasas ruta de salida, se crea un `.md` junto al archivo original.

## Verificar MarkItDown

```powershell
.\.venv\Scripts\markitdown.exe --version
```

## Nota sobre YouTube

Este proyecto instala MarkItDown sin el extra de YouTube para mantener compatibilidad con Python 3.14 en esta estacion.
