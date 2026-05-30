from __future__ import annotations

from PySide6.QtCore import QObject, QTimer

from app.reminder_dialog import ReminderDialog
from app.task_model import Task


class ReminderService(QObject):
    def __init__(self, main_window, tray_controller, interval_ms: int = 1000) -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.tray_controller = tray_controller
        self.timer = QTimer(self)
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self.check_due_tasks)

    def start(self) -> None:
        self.timer.start()
        self.check_due_tasks()

    def stop(self) -> None:
        self.timer.stop()

    def check_due_tasks(self) -> None:
        for task in list(self.main_window.tasks):
            if task.is_due:
                self._notify(task)
                task.mark_reminded()
                self.main_window.save_tasks()
                self.main_window.refresh_tasks()

    def _notify(self, task: Task) -> None:
        title = f"任务提醒：{task.title}"
        body = task.note.strip() or task.reminder_at.strftime("%Y-%m-%d %H:%M:%S")
        self.tray_controller.show_message(title, body)

        dialog = ReminderDialog(task)
        dialog.exec()
