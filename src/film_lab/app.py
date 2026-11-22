"""Desktop entry point, also used by the packaged application."""

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from film_lab import __version__
from film_lab.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Film Lab")
    app.setApplicationVersion(__version__)
    window = MainWindow()
    window.show()
    if "--smoke-test" in sys.argv:
        # Exercise the actual event loop and native dependencies in frozen builds too.
        import cv2
        import numpy as np

        gray = cv2.cvtColor(np.zeros((2, 2, 3), dtype=np.float32), cv2.COLOR_RGB2GRAY)
        if gray.shape != (2, 2):
            return 1
        QTimer.singleShot(200, app.quit)
    return app.exec()
