from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".doc",
    ".pptx",
    ".xlsx",
    ".xls",
    ".html",
    ".htm",
    ".txt",
    ".csv",
    ".json",
    ".xml",
    ".zip",
    ".epub",
    ".msg",
    ".wav",
    ".mp3",
    ".jpg",
    ".jpeg",
    ".jfif",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".jfif", ".png", ".bmp", ".tif", ".tiff", ".webp"}

DOCUMENT_EXTENSIONS = sorted(SUPPORTED_EXTENSIONS - IMAGE_EXTENSIONS)
IMAGE_TYPE_PATTERNS = ["*.jpg", "*.jpeg", "*.jfif", "*.png", "*.bmp", "*.tif", "*.tiff", "*.webp"]
DOCUMENT_TYPE_PATTERNS = [f"*{extension}" for extension in DOCUMENT_EXTENSIONS]
SUPPORTED_TYPE_NAMES = [extension.lstrip(".") for extension in sorted(SUPPORTED_EXTENSIONS)]

DEFAULT_MAX_FILES = 100
DEFAULT_MAX_FILE_SIZE_MB = 100
CSV_FORMULA_PREFIXES = ("=", "+", "-", "@")


@dataclass(frozen=True)
class FileLimits:
    max_files: int = DEFAULT_MAX_FILES
    max_file_size_mb: int = DEFAULT_MAX_FILE_SIZE_MB

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


def safe_filename(filename: str) -> str:
    path = Path(filename).name
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(path).stem).strip("._")
    suffix = re.sub(r"[^A-Za-z0-9.]+", "", Path(path).suffix)
    return f"{stem or 'documento'}{suffix.lower()}"


def safe_stem(name: str) -> str:
    return Path(safe_filename(name)).stem or "documento"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def is_supported_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def validate_file_limits(files: list[Path], limits: FileLimits | None = None) -> None:
    active_limits = limits or FileLimits()
    if len(files) > active_limits.max_files:
        raise ValueError(
            f"Demasiados archivos: {len(files)}. Limite: {active_limits.max_files}."
        )

    oversized = [
        path
        for path in files
        if path.exists() and path.stat().st_size > active_limits.max_file_size_bytes
    ]
    if oversized:
        names = ", ".join(path.name for path in oversized[:5])
        raise ValueError(
            f"Archivo(s) sobre {active_limits.max_file_size_mb} MB: {names}."
        )


def validate_named_sizes(items: list[tuple[str, int]], limits: FileLimits | None = None) -> None:
    active_limits = limits or FileLimits()
    if len(items) > active_limits.max_files:
        raise ValueError(
            f"Demasiados archivos: {len(items)}. Limite: {active_limits.max_files}."
        )

    oversized = [name for name, size in items if size > active_limits.max_file_size_bytes]
    if oversized:
        names = ", ".join(oversized[:5])
        raise ValueError(
            f"Archivo(s) sobre {active_limits.max_file_size_mb} MB: {names}."
        )


def csv_safe(value: object) -> str:
    text = "" if value is None else str(value)
    if text.startswith(CSV_FORMULA_PREFIXES):
        return "'" + text
    return text


def ensure_manifest(path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(",".join(fieldnames) + "\n", encoding="utf-8")


def append_manifest(path: Path, fieldnames: list[str], row: dict[str, object]) -> None:
    ensure_manifest(path, fieldnames)
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow({field: csv_safe(row.get(field, "")) for field in fieldnames})


def read_manifest(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))
