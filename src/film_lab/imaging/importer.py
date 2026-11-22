import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np


def import_page(path: Path, page: int = 0):
    """Return full-resolution linear RGB uint16 pixels and the page count."""
    if getattr(sys, "frozen", False):
        helper = Path(sys._MEIPASS) / "film-decode"
    else:
        helper = Path(__file__).resolve().parents[3] / "build" / "film-decode"
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "pixels.tif"
        result = subprocess.run([helper, path, target, str(page)], capture_output=True, text=True)
        if result.returncode:
            raise ValueError(result.stderr.strip() or "Image decoding failed.")
        pixels = cv2.imread(str(target), cv2.IMREAD_UNCHANGED)
        if pixels is None or pixels.dtype != np.uint16:
            raise ValueError("Could not read the decoded 16-bit image.")
        return cv2.cvtColor(pixels, cv2.COLOR_BGR2RGB), int(result.stdout)
