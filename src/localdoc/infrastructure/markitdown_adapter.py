from __future__ import annotations

from pathlib import Path

from markitdown import MarkItDown


class MarkItDownAdapter:
    def __init__(self) -> None:
        self._converter = MarkItDown()

    def convert(self, source_path: Path) -> str:
        result = self._converter.convert(str(source_path))
        return result.text_content

