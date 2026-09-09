from __future__ import annotations

import re
from pathlib import Path

from localdoc.domain.models import safe_stem


def resolve_available_output_path(output_dir: Path, stem: str, suffix: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    clean_stem = safe_stem(stem)
    clean_suffix = suffix if suffix.startswith(".") else f".{suffix}"
    candidate = output_dir / f"{clean_stem}{clean_suffix}"
    index = 1
    while candidate.exists():
        candidate = output_dir / f"{clean_stem} ({index}){clean_suffix}"
        index += 1
    return candidate


def normalize_display_path(path: Path) -> str:
    return re.sub(r"\\+", r"\\", str(path))

