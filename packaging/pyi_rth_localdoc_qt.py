from __future__ import annotations

import os
import sys
from ctypes import WinDLL

_DLL_DIRECTORY_HANDLES = []
_DLL_HANDLES = []


def _add_dll_path(path: str) -> None:
    if not os.path.isdir(path):
        return
    if hasattr(os, "add_dll_directory"):
        _DLL_DIRECTORY_HANDLES.append(os.add_dll_directory(path))
    os.environ["PATH"] = path + os.pathsep + os.environ.get("PATH", "")


if hasattr(sys, "_MEIPASS"):
    _base_path = sys._MEIPASS
    _add_dll_path(_base_path)
    _add_dll_path(os.path.join(_base_path, "PySide6"))
    _add_dll_path(os.path.join(_base_path, "shiboken6"))

    for _dll_path in (
        os.path.join(_base_path, "shiboken6", "shiboken6.abi3.dll"),
        os.path.join(_base_path, "PySide6", "shiboken6.abi3.dll"),
        os.path.join(_base_path, "PySide6", "Qt6Core.dll"),
        os.path.join(_base_path, "PySide6", "Qt6Gui.dll"),
        os.path.join(_base_path, "PySide6", "Qt6Widgets.dll"),
    ):
        if os.path.exists(_dll_path):
            _DLL_HANDLES.append(WinDLL(_dll_path))
