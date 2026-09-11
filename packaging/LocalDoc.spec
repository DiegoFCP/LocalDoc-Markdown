# -*- mode: python ; coding: utf-8 -*-

from importlib.util import find_spec
from pathlib import Path

from PyInstaller.utils.hooks import collect_all


repo_root = Path(SPECPATH).parent

datas = []
binaries = []
hiddenimports = []

for package_name in ("magika", "markitdown", "pytesseract", "PIL"):
    package_datas, package_binaries, package_hiddenimports = collect_all(package_name)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports

datas.append((str(repo_root / "src" / "localdoc" / "ui" / "resources"), "localdoc/ui/resources"))

hiddenimports += [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
]

shiboken_spec = find_spec("shiboken6")
shiboken_dir = Path(shiboken_spec.origin).parent if shiboken_spec and shiboken_spec.origin else None
if shiboken_dir and shiboken_dir.exists():
    binaries += [(str(path), "shiboken6") for path in shiboken_dir.glob("*.dll")]
    binaries += [(str(path), "PySide6") for path in shiboken_dir.glob("*.dll")]


a = Analysis(
    [str(repo_root / "src" / "localdoc" / "__main__.py")],
    pathex=[str(repo_root / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(repo_root / "packaging" / "pyi_rth_localdoc_qt.py")],
    excludes=["streamlit"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LocalDoc",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(repo_root / "src" / "localdoc" / "ui" / "resources" / "branding" / "localdoc.ico"),
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=["PySide6", "Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll"],
    name="LocalDoc",
)
