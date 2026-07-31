"""
Writable-path resolution for config/logs.

In dev mode (running from source), config and logs live next to the repo,
same as always. Once packaged with PyInstaller (sys.frozen is set), the
app is installed to Program Files - not writable by a standard user - and
a onefile build's own directory is a throwaway temp extraction folder
recreated on every launch anyway. So a frozen build needs a real per-user
writable location instead: %APPDATA%\\SDR Controller on Windows.
"""

import os
import sys


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def user_data_dir() -> str:
    if is_frozen():
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        path = os.path.join(base, "SDR Controller")
    else:
        path = os.path.join(os.path.dirname(__file__), "..")
    os.makedirs(path, exist_ok=True)
    return path


def default_log_folder() -> str:
    return os.path.join(user_data_dir(), "logs") if is_frozen() else "logs"
