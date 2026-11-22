import os
from pathlib import Path

import cv2
import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from film_lab.ui.main_window import MainWindow


def test_import_and_preview(tmp_path):
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    path = tmp_path / "scan.tif"
    frame = np.full((12, 16, 3), 16000, np.uint16)
    assert cv2.imwritemulti(str(path), [frame, frame * 2])
    assert window.load(path)
    first = window.preview.pixmap().toImage()
    window.ev.setValue(10)
    assert first != window.preview.pixmap().toImage()
    assert window.page.maximum() == 2
    window.page.setValue(2)
    assert window.pixels.dtype == np.uint16
    assert window.pixels.shape == (12, 16, 3)
    assert not window.load(tmp_path / "missing.nef")
    assert window.path == path
    window.close()
    app.processEvents()


@pytest.mark.skipif("TEST_NEF" not in os.environ, reason="requires camera NEF")
def test_camera_raw():
    from film_lab.imaging.importer import import_page

    pixels, pages = import_page(Path(os.environ["TEST_NEF"]))
    assert pages == 1 and pixels.dtype == np.uint16 and pixels.std() > 0
