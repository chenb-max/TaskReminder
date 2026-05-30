import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from qfluentwidgets import Theme, setTheme, setThemeColor

from app.main_window import MainWindow
from app.reminder_service import ReminderService
from app.tray import TrayController


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("TaskReminder")
    app.setQuitOnLastWindowClosed(False)
    app.setFont(QFont("Microsoft YaHei UI", 9))
    setTheme(Theme.LIGHT)
    setThemeColor("#2563EB")

    window = MainWindow()
    tray = TrayController(window)
    reminder_service = ReminderService(window, tray)

    window.set_tray_controller(tray)
    window.set_reminder_service(reminder_service)
    tray.show()
    reminder_service.start()

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
