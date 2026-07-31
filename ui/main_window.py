from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt

from .sidebar import Sidebar, PAGES
from .widgets import SidebarHeader, EmergencyStopButton, ConfirmDialog
from .theme_colors import NAVY, BORDER_SUBTLE_DARK
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

        stop_footer = QWidget()
        stop_footer.setAttribute(Qt.WA_StyledBackground, True)
        stop_footer.setObjectName("SidebarFooter")
        stop_footer.setStyleSheet(
            f"#SidebarFooter {{ background: {NAVY}; "
            f"border-top: 1px solid {BORDER_SUBTLE_DARK}; border-right: 1px solid {BORDER_SUBTLE_DARK}; }}"
        )
        stop_footer_layout = QVBoxLayout(stop_footer)
        stop_footer_layout.setContentsMargins(12, 12, 12, 12)
        self.emergency_stop_btn = EmergencyStopButton()
        self.emergency_stop_btn.clicked.connect(self._on_emergency_stop)
        stop_footer_layout.addWidget(self.emergency_stop_btn)
        sidebar_layout.addWidget(stop_footer)

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
        header_height = self.sidebar_header.height()
        for page in self.pages.values():
            page.header.setFixedHeight(header_height)

    def _on_page_selected(self, name: str):
        self.stack.setCurrentWidget(self.pages[name])

    def _on_emergency_stop(self):
        confirmed = ConfirmDialog.ask(
            self,
            "Emergency Stop",
            "Immediately turn off the device output?",
            confirm_text="Turn Off",
            cancel_text="Cancel",
            danger=True,
        )
        if not confirmed:
            return
        self.app.device.turn_output_off()

    def closeEvent(self, event):
        self.app.shutdown()
        event.accept()
