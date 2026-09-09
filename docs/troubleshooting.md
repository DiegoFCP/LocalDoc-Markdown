# Troubleshooting

## Tesseract Is Not Detected

Check:

```powershell
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
```

If it works, open the desktop app and select `Elegir EXE`.

## Spanish OCR Does Not Work

Make sure `spa` appears in:

```powershell
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
```

If only `eng` appears, install Spanish trained data in Tesseract's `tessdata` folder.

## Audio Warning About ffmpeg

This warning is expected when `ffmpeg` is not installed:

```text
Couldn't find ffmpeg or avconv
```

It affects audio/video workflows, not regular PDF, Office, HTML, text, or image OCR conversions.

## PowerShell Execution Policy

Use:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Setup-Environment.ps1
```

This bypasses policy only for that command.

## GitHub Release EXE Does Not OCR Images

The EXE includes the Python OCR wrapper but does not bundle the native Tesseract OCR engine. Install Tesseract separately on Windows.
