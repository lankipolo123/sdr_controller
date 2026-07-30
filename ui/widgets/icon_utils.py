from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt


def tint_pixmap(pixmap: QPixmap, color: str) -> QPixmap:
    """Recolor a monochrome icon's opaque pixels to `color`, keeping its alpha."""
    tinted = QPixmap(pixmap.size())
    tinted.fill(Qt.transparent)
    painter = QPainter(tinted)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(tinted.rect(), QColor(color))
    painter.end()
    return tinted
