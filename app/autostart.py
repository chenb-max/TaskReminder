from __future__ import annotations

import sys
from pathlib import Path

try:
    import winreg
except ImportError:  # pragma: no cover - Windows-only behavior
    winreg = None


RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_RUN_NAME = "TaskReminder"


def is_supported() -> bool:
    return sys.platform.startswith("win") and winreg is not None


def get_startup_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{Path(sys.executable)}"'

    entrypoint = Path(__file__).resolve().parents[1] / "main.py"
    return f'"{Path(sys.executable)}" "{entrypoint}"'


def is_enabled() -> bool:
    if not is_supported():
        return False

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_RUN_NAME)
            return True
    except OSError:
        return False


def set_enabled(enabled: bool) -> None:
    if not is_supported():
        raise RuntimeError("开机自启仅支持 Windows。")

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        RUN_KEY_PATH,
        0,
        winreg.KEY_SET_VALUE,
    ) as key:
        if enabled:
            winreg.SetValueEx(key, APP_RUN_NAME, 0, winreg.REG_SZ, get_startup_command())
        else:
            try:
                winreg.DeleteValue(key, APP_RUN_NAME)
            except FileNotFoundError:
                pass
