"""Verify the real Qt event loop and compiled image dependencies can start."""

import os
import subprocess
import sys


def test_application_starts_and_exits():
    result = subprocess.run(
        [sys.executable, "-m", "film_lab", "--smoke-test"],
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
