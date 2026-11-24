from pathlib import Path

import numpy as np
import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from film_lab.ui.main_window import MainWindow


@pytest.fixture
def loaded(monkeypatch):
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    app.processEvents()
    pixels = np.array([[[0, 16384, 32768], [65535, 64, 16384]]], dtype=np.uint16)
    monkeypatch.setattr("film_lab.ui.main_window.import_page", lambda *_: (pixels, 1))
    assert window.load(Path("reference.tif"))
    app.processEvents()
    yield window
    window.close()


def test_drag_pan(loaded):
    view = loaded.preview
    view.zoom = 4
    start = view.rect().center()
    delta = QPoint(45, -32)
    initial = view.image_rect()
    left = Qt.MouseButton.LeftButton
    QTest.mousePress(view, left, pos=start)
    QTest.mouseMove(view, start + delta)
    assert view.image_rect().x() == pytest.approx(initial.x() + delta.x())
    assert view.image_rect().y() == pytest.approx(initial.y() + delta.y())
    QTest.mouseRelease(view, left, pos=start + delta)
    end = view.image_rect()
    QTest.mouseMove(view, start)
    assert view.image_rect() == end
    assert view.zoom == 4


@pytest.mark.parametrize(
    ("slider", "expected"),
    [
        (0, [(0, 137, 188), (255, 3, 137)]),
        (10, [(0, 188, 255), (255, 6, 188)]),
        (-10, [(0, 99, 137), (188, 2, 99)]),
    ],
)
def test_exposure_and_rgb_bins(loaded, slider, expected):
    loaded.ev.setValue(slider)
    image = loaded.preview.pixmap().toImage()
    assert [image.pixelColor(x, 0).getRgb()[:3] for x in range(2)] == expected
    bins = np.zeros((3, 256), dtype=int)
    for pixel in expected:
        for channel, value in enumerate(pixel):
            bins[channel, value] += 1
    np.testing.assert_array_equal(loaded.histogram.counts, bins)
