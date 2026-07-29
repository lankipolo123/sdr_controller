from ui.base_page import BasePage
from ui.widgets import TerminalWidget


class CommunicationPage(BasePage):
    def __init__(self, app_controller, parent=None):
        super().__init__("Communication", "communication", app_controller, parent)

        layout = self.content_layout

        self.terminal = TerminalWidget()
        layout.addWidget(self.terminal)

        self.app.connection.raw_rx.connect(self.terminal.log_rx)
        self.app.connection.frame_received.connect(lambda f: self.terminal.log_info(f.describe()))
        self.app.connection.error.connect(self.terminal.log_error)
        self.app.device.command_timeout.connect(self.terminal.log_error)
        self.app.connection.connected_changed.connect(
            lambda c: self.terminal.log_info("Connected" if c else "Disconnected")
        )

        self._last_seen_command = None
        self.app.device_state.changed.connect(self._maybe_log_tx)

    def _maybe_log_tx(self):
        cmd = self.app.device_state.data.last_command
        if cmd != self._last_seen_command:
            self._last_seen_command = cmd
            self.terminal.log_info(f"Command issued: {cmd}")
