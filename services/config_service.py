import json
import os

DEFAULT_CONFIG = {
    "com_port": "",
    "baud_rate": 115200,
    "module_address": 0,
    "auto_connect": False,
    "log_folder": "logs",
}

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")


class ConfigService:
    def __init__(self, path: str = CONFIG_PATH):
        self.path = path
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    loaded = json.load(f)
                self.data.update(loaded)
            except (json.JSONDecodeError, OSError):
                pass  # fall back to defaults silently; don't crash the app on a bad config file
        return self.data

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
