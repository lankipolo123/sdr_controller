from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget

from .sidebar import Sidebar, PAGES
from .widgets import SidebarHeader
from .pages import DashboardPage, DeviceControlPage, CommunicationPage


class MainWindow(QMainWindow):
    def __init__(self, app_controller):
        super().__init__()
        self.app = app_controller
        self.setWindowTitle("SDR Noise Generator Controller")
        self.resize(1000, 680)

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar_column = QWidget()
        sidebar_column.setFixedWidth(180)
        sidebar_layout = QVBoxLayout(sidebar_column)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        self.sidebar_header = SidebarHeader()
        sidebar_layout.addWidget(self.sidebar_header)

        self.sidebar = Sidebar()
        sidebar_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()

        self.pages = {
            "Dashboard": DashboardPage(self.app),
            "Device Control": DeviceControlPage(self.app),
            "Communication": CommunicationPage(self.app),
        }
        for name in PAGES:
            self.stack.addWidget(self.pages[name])

        self.sidebar.page_selected.connect(self._on_page_selected)

        layout.addWidget(sidebar_column)
        layout.addWidget(self.stack)
        self.setCentralWidget(central)

        self._sync_header_heights()

    def _sync_header_heights(self):
        """
        Header height was previously a hardcoded number measured once on
        one machine — it drifted out of alignment with the sidebar on
        machines where Qt computes row height differently (font
        rendering, DPI, OS). Fix: read the sidebar's real, live row
        height and apply it to every page's header directly, so they're
        guaranteed to match regardless of platform.
        """
        row_height = self.sidebar.row_height()
        for page in self.pages.values():
            page.header.setFixedHeight(row_height)

    def _on_page_selected(self, name: str):
        self.stack.setCurrentWidget(self.pages[name])

    def closeEvent(self, event):
        self.app.shutdown()
        event.accept()
