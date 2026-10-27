"""Build MahyarCompressor.exe with PyInstaller.

    python scripts/build.py            # single portable .exe  (dist/MahyarCompressor.exe)
    python scripts/build.py --onedir   # folder build, starts faster (dist/MahyarCompressor/)
"""
import sys
from pathlib import Path

import PyInstaller.__main__ as pyi

ROOT = Path(__file__).resolve().parent.parent
ICON_PATH = ROOT / "assets" / "icon.ico"

EXCLUDES = [  # Qt / stdlib parts we never use -> smaller exe
    "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtQuickWidgets",
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.QtPdf", "PySide6.QtSvg",
    "PySide6.QtSql", "PySide6.QtTest", "PySide6.QtMultimedia", "PySide6.QtOpenGL",
    "PySide6.Qt3DCore", "PySide6.QtCharts", "PySide6.QtDataVisualization",
    "tkinter", "unittest", "pydoc",
]

args = [
    str(ROOT / "run.py"),
    "--name", "MahyarCompressor",
    "--noconfirm", "--clean", "--windowed",
    "--onedir" if "--onedir" in sys.argv else "--onefile",
    "--paths", str(ROOT / "src"),
    "--collect-all", "imageio_ffmpeg",          # bundles the ffmpeg binary
    "--distpath", str(ROOT / "dist"),
    "--workpath", str(ROOT / "build"),
    "--specpath", str(ROOT / "build"),
]

if ICON_PATH.exists():
    args += ["--icon", str(ICON_PATH)]

for m in EXCLUDES:
    args += ["--exclude-module", m]

pyi.run(args)
