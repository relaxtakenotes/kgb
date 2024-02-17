import sys
from cx_Freeze import setup, Executable
import subprocess
import os
from pathlib import Path
import shutil
import traceback

build_exe_options = {
    "include_files": [
        "config.json.example"
    ],
    "includes": ["commands"],
    "excludes": ["scipy", "llvmlite", "sympy", "test", "numba", "setuptools", "Pyinstaller", "tk8.6", "_pytest", "docutils"],
    "build_exe": "../build/"
}

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="kgb",
    version="0.1",
    description="KGB",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base = base)],
)