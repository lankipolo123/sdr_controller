"""
Shared page scaffold. Every page in ui/pages/ should subclass BasePage
instead of QWidget directly.

Why this exists: previously every page built its own QVBoxLayout(self)
with Qt's default margins, then added PageHeader as the first item. That
left a margin around the header, so it looked "contained inside" the
page rather than spanning edge-to-edge the way the sidebar spans the
full height. BasePage fixes this once, centrally: the outer layout has
zero margins so the header genuinely touches the top/left/right edges
of the page area, and a separate inner `content_layout` (with its own
padding) is where each page adds its real widgets.

Also owns the header's Close Application button behavior, since PageHeader
itself has no knowledge of the app/connection — closing here means
disconnecting the device (if connected) and quitting the app, after a
confirmation so a stray click doesn't kill an active bench test.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication

from ui.widgets import PageHeader, ConfirmDialog

CONTENT_MARGIN = 20


class BasePage(QWidget):
    def __init__(self, title: str, icon_key: str, app_controller=None, parent=None):
        super().__init__(parent)
        self.app = app_controller

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.header = PageHeader(title, icon_key)
        self.header.close_requested.connect(self._on_close_requested)
        outer.addWidget(self.header)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(
            CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN
        )
        outer.addWidget(content)

    def _on_close_requested(self):
        confirmed = ConfirmDialog.ask(
            self,
            "Close Application",
            "Disconnect from the device and close the app?",
            confirm_text="Close",
            cancel_text="Cancel",
            danger=True,
        )
        if not confirmed:
            return
        if self.app is not None and self.app.connection.is_connected():
            self.app.connection.disconnect()
        QApplication.instance().quit()
