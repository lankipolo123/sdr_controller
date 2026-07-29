import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from controller import AppController
from ui.main_window import MainWindow

ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "icons", "app_icon.png")


def run():
    qt_app = QApplication(sys.argv)
    if os.path.exists(ICON_PATH):
        qt_app.setWindowIcon(QIcon(ICON_PATH))
    app_controller = AppController()
    window = MainWindow(app_controller)
    window.show()
    sys.exit(qt_app.exec())
