# MarkItDown Workbench

Monorepo local para convertir documentos a Markdown usando Microsoft MarkItDown, con interfaz de escritorio, interfaz Streamlit, pipeline por carpetas y OCR local con Tesseract para imagenes.

## Contenido

```text
apps/desktop/app.py      Aplicacion de escritorio Tkinter
apps/streamlit/app.py    Interfaz web local con Streamlit
scripts/                 Setup, ejecucion, conversion y build
docs/                    Guias de uso
examples/                Archivos de prueba
work/                    Datos locales generados en ejecucion
```

## Requisitos

- Windows
- Python 3.10 a 3.14
- Tesseract OCR instalado para imagenes

Tesseract verificado en esta estacion:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Idiomas recomendados:

```text
spa+eng
```

## Setup

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Setup-Environment.ps1
```

## Ejecutar app de escritorio

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Run-Desktop.ps1
```

## Ejecutar Streamlit

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Run-Streamlit.ps1
```

Abrir:

```text
http://127.0.0.1:8501
```

## Convertir un archivo por CLI

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Convert-ToMarkdown.ps1 "C:\ruta\archivo.pdf"
```

## Pipeline por carpetas

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Process-MarkitdownInbox.ps1
```

Carpetas por defecto:

```text
work\pipeline\input
work\pipeline\output
work\pipeline\logs
```

## Generar EXE

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Build-DesktopExe.ps1
```

El ejecutable queda en:

```text
dist\MarkItDownDesktop.exe
```

## GitHub

Cuando crees el repositorio en GitHub, agrega el remoto y sube:

```powershell
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git branch -M main
git push -u origin main
```
