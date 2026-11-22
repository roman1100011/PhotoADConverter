"""Build a self-contained desktop application using the current environment."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--windowed",
            "--onedir",
            "--name",
            "Film Lab",
            "--paths",
            str(ROOT / "src"),
            "--distpath",
            str(ROOT / "dist"),
            "--workpath",
            str(ROOT / "build" / "pyinstaller"),
            "--specpath",
            str(ROOT / "build"),
            "--osx-bundle-identifier",
            "local.filmlab.desktop",
            str(ROOT / "scripts" / "launcher.py"),
        ],
        cwd=ROOT,
        env={**os.environ, "PYINSTALLER_CONFIG_DIR": str(ROOT / "build" / "cache")},
        check=True,
    )


if __name__ == "__main__":
    main()
