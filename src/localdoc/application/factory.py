from __future__ import annotations

from localdoc.application.conversion_manager import ConversionManager
from localdoc.application.history_service import HistoryService
from localdoc.application.settings_service import SettingsService
from localdoc.infrastructure.database import Database
from localdoc.infrastructure.paths import AppPaths, get_default_paths
from localdoc.infrastructure.repositories import JobRepository
from localdoc.workers.conversion_worker import ProcessConversionRunner


def build_settings_service(paths: AppPaths | None = None) -> SettingsService:
    active_paths = paths or get_default_paths()
    active_paths.ensure()
    return SettingsService(active_paths)


def build_conversion_manager(paths: AppPaths | None = None) -> ConversionManager:
    active_paths = paths or get_default_paths()
    active_paths.ensure()
    settings_service = SettingsService(active_paths)
    settings = settings_service.load()
    history = HistoryService(JobRepository(Database(active_paths.database_file)))
    return ConversionManager(
        history_service=history,
        settings=settings,
        conversion_runner=ProcessConversionRunner(),
    )
