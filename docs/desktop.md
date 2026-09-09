# App de escritorio

## Ejecutar desde fuente

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Run-Desktop.ps1
```

## Generar EXE

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Build-DesktopExe.ps1
```

El ejecutable queda en:

```text
dist\MarkItDownDesktop.exe
```

## Funciones

- Agregar documentos individuales.
- Agregar imagenes para OCR.
- Agregar carpetas completas.
- Elegir carpeta de salida.
- Convertir documentos a Markdown con MarkItDown.
- Convertir imagenes a Markdown con Tesseract OCR.
- Abrir carpeta de resultados.
- Abrir historial CSV.

## OCR

La app busca automaticamente:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
C:\Program Files (x86)\Tesseract-OCR\tesseract.exe
```

Idioma recomendado:

```text
spa+eng
```

Si Tesseract no aparece, usa `Elegir EXE` y selecciona `tesseract.exe`. Para seleccionar imagenes usa `Agregar imagenes`.
