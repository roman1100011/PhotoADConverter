from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from film_lab.imaging.importer import import_page
from film_lab.ui.preview import Histogram, Preview


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Film Lab")
        self.resize(1120, 760)
        self.path = self.pixels = self.thumbnail = None
        body = QWidget()
        layout = QHBoxLayout(body)
        self.preview = Preview()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setStyleSheet("background:#181818;color:white")
        self.preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        layout.addWidget(self.preview, 1)
        controls = QWidget()
        panel = QVBoxLayout(controls)
        button = QPushButton("Import image…")
        button.clicked.connect(self.choose)
        panel.addWidget(button)
        panel.addWidget(QLabel("TIFF page"))
        self.page = QSpinBox()
        self.page.setRange(1, 1)
        self.page.setEnabled(False)
        self.page.valueChanged.connect(lambda value: self.load(self.path, value - 1))
        panel.addWidget(self.page)
        panel.addWidget(QLabel("RGB histogram"))
        self.histogram = Histogram()
        panel.addWidget(self.histogram)
        self.exposure_label = QLabel("Exposure  0.0 EV")
        panel.addWidget(self.exposure_label)
        self.ev = QSlider(Qt.Orientation.Horizontal)
        self.ev.setRange(-30, 30)
        self.ev.setTickInterval(10)
        self.ev.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.ev.valueChanged.connect(self.render)
        panel.addWidget(self.ev)
        scale = QHBoxLayout()
        scale.setContentsMargins(0, 0, 0, 0)
        for value in range(-3, 4):
            if value != -3:
                scale.addStretch()
            scale.addWidget(QLabel(f"{value:+d}" if value else "0"))
        panel.addLayout(scale)
        panel.addStretch()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(controls)
        scroll.setFixedWidth(225)
        layout.addWidget(scroll)
        self.setCentralWidget(body)
        menu = self.menuBar().addMenu("File")
        action = QAction("Import image…", self)
        action.setShortcut(QKeySequence.StandardKey.Open)
        action.triggered.connect(self.choose)
        menu.addAction(action)
        menu.addAction("Quit Film Lab", self.close, QKeySequence.StandardKey.Quit)

    def choose(self):
        name, _ = QFileDialog.getOpenFileName(
            self, "Import image", "", "Images (*.tif *.tiff *.nef *.TIF *.TIFF *.NEF)"
        )
        if name:
            self.load(Path(name))

    def load(self, path, page=0):
        try:
            pixels, pages = import_page(path, page)
        except (ValueError, OSError) as error:
            self.statusBar().showMessage(str(error))
            self.page.blockSignals(True)
            self.page.setValue(getattr(self, "loaded_page", 0) + 1)
            self.page.blockSignals(False)
            return False
        self.preview.reset_view()
        self.loaded_page = page
        self.path, self.pixels = path, pixels
        height, width = pixels.shape[:2]
        scale = min(1, 1600 / max(height, width))
        self.thumbnail = (
            cv2.resize(
                pixels,
                (max(1, round(width * scale)), max(1, round(height * scale))),
                interpolation=cv2.INTER_AREA,
            ).astype(np.float32)
            / 65535
        )
        self.page.blockSignals(True)
        self.page.setRange(1, pages)
        self.page.setValue(page + 1)
        self.page.setEnabled(pages > 1)
        self.page.blockSignals(False)
        self.ev.setValue(0)
        self.statusBar().showMessage(f"{path.name}   {width} × {height}")
        self.render()
        return True

    def render(self):
        self.exposure_label.setText(f"Exposure  {self.ev.value() / 10:+.1f} EV")
        if self.thumbnail is None:
            return
        linear = np.clip(self.thumbnail * (2 ** (self.ev.value() / 10)), 0, 1)
        rgb = np.where(linear <= 0.0031308, 12.92 * linear, 1.055 * linear ** (1 / 2.4) - 0.055)
        data = (rgb * 255 + 0.5).astype(np.uint8)
        h, w = data.shape[:2]
        image = QImage(data.data, w, h, data.strides[0], QImage.Format.Format_RGB888)
        self.preview.setPixmap(QPixmap.fromImage(image))
        self.histogram.set_pixels(data)
