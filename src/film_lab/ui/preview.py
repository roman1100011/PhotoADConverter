import numpy as np
from PySide6.QtCore import QEvent, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QLabel, QWidget


class Preview(QLabel):
    def __init__(self):
        super().__init__("Import a TIFF or Nikon NEF")
        self.reset_view()

    def reset_view(self):
        self.drag_at = None
        self.unsetCursor()
        self.zoom = 1.0
        self.focus = QPointF(0.5, 0.5)
        self.update()

    def image_rect(self):
        image = self.pixmap()
        scale = min(self.width() / image.width(), self.height() / image.height()) * self.zoom
        w, h = image.width() * scale, image.height() * scale

        def origin(view, span, focus):
            if span <= view:
                return (view - span) / 2
            return max(view - span, min(0, view / 2 - span * focus))

        return QRectF(
            origin(self.width(), w, self.focus.x()), origin(self.height(), h, self.focus.y()), w, h
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.pixmap().isNull():
            rect = self.image_rect()
            if rect.contains(event.position()) and (
                rect.width() > self.width() or rect.height() > self.height()
            ):
                self.drag_at = event.position()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_at is None or not event.buttons() & Qt.MouseButton.LeftButton:
            return super().mouseMoveEvent(event)
        rect = self.image_rect()
        delta = event.position() - self.drag_at
        self.drag_at = event.position()
        self.focus = QPointF(
            (self.width() / 2 - rect.x() - delta.x()) / rect.width(),
            (self.height() / 2 - rect.y() - delta.y()) / rect.height(),
        )
        self.update()
        event.accept()

    def mouseReleaseEvent(self, event):
        if self.drag_at is not None and event.button() == Qt.MouseButton.LeftButton:
            self.drag_at = None
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def event(self, event):
        if (
            event.type() == QEvent.Type.NativeGesture
            and event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture
            and not self.pixmap().isNull()
            and self.width()
            and self.height()
        ):
            rect = self.image_rect()
            at = event.position()
            old = self.zoom
            self.zoom = min(16, max(0.25, old * (1 + event.value())))
            ratio = self.zoom / old
            self.focus = QPointF(
                ((at.x() - rect.x()) * ratio + self.width() / 2 - at.x()) / (rect.width() * ratio),
                ((at.y() - rect.y()) * ratio + self.height() / 2 - at.y())
                / (rect.height() * ratio),
            )
            self.update()
            event.accept()
            return True
        return super().event(event)

    def paintEvent(self, event):
        image = self.pixmap()
        if image.isNull():
            return super().paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#181818"))
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(self.image_rect(), image, QRectF(image.rect()))
        painter.end()


class Histogram(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(82)
        self.counts = np.zeros((3, 256), dtype=int)
        self.setAccessibleName("RGB histogram of the exposure-adjusted preview")

    def set_pixels(self, rgb):
        self.counts = np.stack(
            [np.bincount(channel.ravel(), minlength=256) for channel in rgb.transpose(2, 0, 1)]
        )
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#181818"))
        heights = np.log1p(self.counts)
        heights *= (self.height() - 3) / max(1, heights.max())
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
        for bins, color in zip(heights, ["#ed4646", "#40cc62", "#5282e8"]):
            path = QPainterPath()
            for i, value in enumerate(bins):
                point = QPointF(i * (self.width() - 1) / 255, self.height() - 1 - value)
                if i == 0:
                    path.moveTo(point)
                else:
                    path.lineTo(point)
            p.setPen(QColor(color))
            p.drawPath(path)
        p.end()
