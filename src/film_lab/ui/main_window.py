from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    """Launchable foundation; editing controls arrive with the processing pipeline."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Film Lab")
        self.resize(1120, 760)
        self.setMinimumSize(720, 480)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.addStretch()
        title = QLabel("Film Lab")
        title.setStyleSheet("font-size: 36px; font-weight: 600;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        subtitle = QLabel("A workspace for your scanned film negatives")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        note = QLabel("Application foundation ready. Image editing is coming next.")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()
        self.setCentralWidget(content)

        quit_action = QAction("Quit Film Lab", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        self.menuBar().addMenu("File").addAction(quit_action)
        self.statusBar().showMessage("Ready · Development build 0.1.0")
