from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon


class TrayController(QObject):
    def __init__(self, main_window) -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.tray_icon = QSystemTrayIcon(self._icon(), self)
        self.tray_icon.setToolTip("TaskReminder")
        self.tray_icon.activated.connect(self._on_activated)
        self._build_menu()

    def show(self) -> None:
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()

    def hide(self) -> None:
        self.tray_icon.hide()

    def show_message(self, title: str, message: str) -> None:
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                8000,
            )

    def quit_app(self) -> None:
        self.main_window.allow_quit = True
        self.hide()
        QApplication.quit()

    def _build_menu(self) -> None:
        menu = QMenu()

        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.main_window.show_from_tray)
        menu.addAction(show_action)

        menu.addSeparator()

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.main_window.show_from_tray()

    def _icon(self) -> QIcon:
        app = QApplication.instance()
        if app is None:
            return QIcon()
        return app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
