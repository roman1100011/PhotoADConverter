import numpy as np
import pytest
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QNativeGestureEvent, QPointingDevice
from PySide6.QtWidgets import QApplication

from film_lab.ui.main_window import MainWindow


def test_pinch_and_exposure_histogram(monkeypatch):
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    app.processEvents()
    rgb = np.full((64, 96, 3), [1000, 4000, 16000], dtype=np.uint16)
    monkeypatch.setattr("film_lab.ui.main_window.import_page", lambda *_: (rgb, 1))
    from pathlib import Path

    window.load(Path("film.tif"))
    view = window.preview
    at = QPointF(view.rect().center())

    def pinch(amount):
        event = QNativeGestureEvent(
            Qt.NativeGestureType.ZoomNativeGesture,
            QPointingDevice.primaryPointingDevice(),
            2,
            at,
            at,
            at,
            amount,
            QPointF(),
        )
        QApplication.sendEvent(view, event)
        assert event.isAccepted()

    initial = view.image_rect()
    pinch(0.5)
    assert view.image_rect().width() == pytest.approx(initial.width() * 1.5)
    pinch(-1 / 3)
    assert view.image_rect().width() == pytest.approx(initial.width())
    pinch(0.25)
    before = window.histogram.counts.copy()
    assert (before.sum(axis=1) == 64 * 96).all()
    assert np.all(np.diff(before.argmax(axis=1)) > 0)
    window.ev.setValue(10)
    assert np.all(window.histogram.counts.argmax(axis=1) > before.argmax(axis=1))
    assert "+1.0 EV" in window.exposure_label.text()
    assert view.zoom == 1.25
    window.load(Path("next.tif"))
    assert view.zoom == 1
    window.close()
