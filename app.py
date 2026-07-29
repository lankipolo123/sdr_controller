import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from controller import AppController
from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen

ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "icons", "app_icon.png")


def run():
    qt_app = QApplication(sys.argv)
    if os.path.exists(ICON_PATH):
        qt_app.setWindowIcon(QIcon(ICON_PATH))

    splash = SplashScreen()
    splash.show()
    qt_app.processEvents()

    splash.set_progress(20, "Loading configuration...")
    qt_app.processEvents()
    app_controller = AppController()

    splash.set_progress(70, "Building interface...")
    qt_app.processEvents()
    window = MainWindow(app_controller)

    splash.set_progress(100, "Ready")
    qt_app.processEvents()

    window.show()
    splash.close()
    sys.exit(qt_app.exec())
