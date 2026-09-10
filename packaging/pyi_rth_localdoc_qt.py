from __future__ import annotations

import os
import sys

_DLL_DIRECTORY_HANDLES = []


def _add_dll_path(path: str) -> None:
    if not os.path.isdir(path):
        return
    if hasattr(os, "add_dll_directory"):
        _DLL_DIRECTORY_HANDLES.append(os.add_dll_directory(path))
    os.environ["PATH"] = path + os.pathsep + os.environ.get("PATH", "")


if hasattr(sys, "_MEIPASS"):
    _base_path = sys._MEIPASS
    _add_dll_path(os.path.join(_base_path, "PySide6"))
    _add_dll_path(os.path.join(_base_path, "shiboken6"))
