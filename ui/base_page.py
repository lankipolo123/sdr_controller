from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication

from ui.widgets import PageHeader, ConfirmDialog

CONTENT_MARGIN = 16
CONTENT_SPACING = 12


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
        self.content_layout.setSpacing(CONTENT_SPACING)
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
