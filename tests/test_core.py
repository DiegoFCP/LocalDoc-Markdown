from __future__ import annotations

import csv

import pytest

from localdoc_markdown.core import (
    FileLimits,
    append_manifest,
    csv_safe,
    safe_filename,
    safe_stem,
    sha256_bytes,
    validate_file_limits,
    validate_named_sizes,
)


def test_safe_filename_keeps_extension_and_removes_path_parts() -> None:
    assert safe_filename("../Mi documento raro!!.pdf") == "Mi_documento_raro.pdf"


def test_safe_stem_has_fallback() -> None:
    assert safe_stem("///") == "documento"


def test_sha256_bytes_is_uppercase() -> None:
    assert sha256_bytes(b"localdoc").isupper()


@pytest.mark.parametrize("value", ["=cmd", "+sum", "-10", "@link"])
def test_csv_safe_escapes_formula_prefixes(value: str) -> None:
    assert csv_safe(value).startswith("'")


def test_append_manifest_writes_safe_csv(tmp_path) -> None:
    manifest = tmp_path / "manifest.csv"
    append_manifest(
        manifest,
        ["source_name", "error"],
        {"source_name": "=bad.xlsx", "error": "@boom"},
    )

    with manifest.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["source_name"] == "'=bad.xlsx"
    assert rows[0]["error"] == "'@boom"


def test_validate_file_limits_rejects_too_many_files(tmp_path) -> None:
    files = []
    for index in range(3):
        path = tmp_path / f"{index}.txt"
        path.write_text("x", encoding="utf-8")
        files.append(path)

    with pytest.raises(ValueError, match="Demasiados archivos"):
        validate_file_limits(files, FileLimits(max_files=2, max_file_size_mb=1))


def test_validate_file_limits_rejects_oversized_file(tmp_path) -> None:
    path = tmp_path / "large.txt"
    path.write_bytes(b"x" * 11)

    with pytest.raises(ValueError, match="sobre 0 MB"):
        validate_file_limits([path], FileLimits(max_files=1, max_file_size_mb=0))


def test_validate_named_sizes_rejects_oversized_upload() -> None:
    with pytest.raises(ValueError, match="large.pdf"):
        validate_named_sizes([("large.pdf", 11)], FileLimits(max_files=1, max_file_size_mb=0))
