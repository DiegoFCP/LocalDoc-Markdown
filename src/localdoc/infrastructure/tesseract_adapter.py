from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytesseract
from PIL import Image

DEFAULT_TESSERACT_PATHS = [
    Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
]


class TesseractAdapter:
    def __init__(self, executable: Path | None = None) -> None:
        self.executable = executable or self.detect()

    def detect(self) -> Path | None:
        path_from_env = shutil.which("tesseract")
        if path_from_env:
            return Path(path_from_env)
        for path in DEFAULT_TESSERACT_PATHS:
            if path.exists():
                return path
        return None

    def is_available(self) -> bool:
        return self.executable is not None and self.executable.exists()

    def available_languages(self) -> list[str]:
        if not self.is_available():
            return []
        completed = subprocess.run(
            [str(self.executable), "--list-langs"],
            capture_output=True,
            check=False,
            text=True,
            timeout=15,
        )
        if completed.returncode != 0:
            return []
        return [
            line.strip()
            for line in completed.stdout.splitlines()
            if line.strip() and not line.lower().startswith("list of available")
        ]

    def extract_text(self, source_path: Path, language: str) -> str:
        if not self.is_available():
            raise RuntimeError("Tesseract OCR no esta instalado o no fue detectado.")
        pytesseract.pytesseract.tesseract_cmd = str(self.executable)
        with Image.open(source_path) as image:
            return pytesseract.image_to_string(image, lang=language)

