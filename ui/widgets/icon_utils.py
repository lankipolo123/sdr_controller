from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QRectF


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


def standard_icon_pixmap(icon_enum, size: int, tint_color: str) -> QPixmap:
    """Qt's built-in standard icon (QStyle.SP_*), tinted to `tint_color`.

    Only works well for icons that are genuinely line-art with real
    transparent gaps (arrows, checkmarks, simple glyphs) - flood-filling
    the opaque shape with one color is what "tint" means here. Detailed
    multi-tone standard icons (SP_ComputerIcon, SP_DriveNetIcon, the
    file-dialog icons) collapse into a solid blob when tinted since their
    detail comes from shading, not transparency - don't use those here."""
    from PySide6.QtWidgets import QApplication

    style = QApplication.instance().style()
    pixmap = style.standardIcon(icon_enum).pixmap(size, size)
    return tint_pixmap(pixmap, tint_color)


def grid_icon_pixmap(size: int, color: str) -> QPixmap:
    """A simple hand-drawn 2x2 grid glyph for "Dashboard/overview" - none
    of Qt's built-in standard icons have a real dashboard/grid concept
    that survives tinting, so this is drawn directly instead of gambling
    on another SP_* enum."""
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(color))
    gap = size * 0.16
    cell = (size - gap * 3) / 2
    radius = cell * 0.25
    for row in range(2):
        for col in range(2):
            x = gap + col * (cell + gap)
            y = gap + row * (cell + gap)
            painter.drawRoundedRect(QRectF(x, y, cell, cell), radius, radius)
    painter.end()
    return pm


def _nav_style_icons():
    """Qt standard icons used for nav (sidebar + page header), picked
    specifically because they tint cleanly (see standard_icon_pixmap).
    "dashboard" isn't here - it uses grid_icon_pixmap() instead."""
    from PySide6.QtWidgets import QStyle
    return {
        "device_control": QStyle.SP_TitleBarNormalButton,
        "communication": QStyle.SP_ToolBarHorizontalExtensionButton,
    }


NAV_ICONS = _nav_style_icons()


def nav_icon_pixmap(icon_key: str, size: int, color: str) -> QPixmap | None:
    """Single entry point for the sidebar/page-header icon set — handles
    both the hand-drawn dashboard icon and the tinted standard icons."""
    if icon_key == "dashboard":
        return grid_icon_pixmap(size, color)
    enum = NAV_ICONS.get(icon_key)
    if enum is None:
        return None
    return standard_icon_pixmap(enum, size, color)
