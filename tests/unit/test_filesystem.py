from __future__ import annotations

from pathlib import Path

from localdoc.infrastructure.filesystem import resolve_available_output_path


def test_resolve_available_output_path_avoids_collisions(tmp_path: Path) -> None:
    first = tmp_path / "Documento.md"
    first.write_text("existing", encoding="utf-8")

    resolved = resolve_available_output_path(tmp_path, "Documento", ".md")

    assert resolved.name == "Documento (1).md"
