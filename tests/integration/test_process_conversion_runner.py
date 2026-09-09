from __future__ import annotations

from pathlib import Path

from localdoc.domain.models import AppSettings, ConversionJob
from localdoc.workers.conversion_worker import ProcessConversionRunner


def test_process_runner_converts_text_file(tmp_path: Path) -> None:
    source = tmp_path / "nota.txt"
    source.write_text("Hola LocalDoc", encoding="utf-8")
    settings = AppSettings(output_dir=tmp_path / "out", conversion_timeout_seconds=30)
    runner = ProcessConversionRunner()
    job = ConversionJob(source)

    result = runner.run(job, settings)

    assert result.error == ""
    assert result.output_path is not None
    assert result.output_path.exists()
    assert "Hola LocalDoc" in result.output_path.read_text(encoding="utf-8")
    assert result.source_hash


def test_process_runner_reports_timeout(tmp_path: Path) -> None:
    source = tmp_path / "nota.txt"
    source.write_text("Hola LocalDoc", encoding="utf-8")
    settings = AppSettings(output_dir=tmp_path / "out", conversion_timeout_seconds=0)
    runner = ProcessConversionRunner()
    job = ConversionJob(source)

    result = runner.run(job, settings)

    assert result.timed_out is True
    assert result.output_path is None
