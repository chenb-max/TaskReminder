from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QVBoxLayout
from qfluentwidgets import BodyLabel, CardWidget, CaptionLabel, PrimaryPushButton, StrongBodyLabel

from app.task_model import RepeatType, Task


class ReminderDialog(QDialog):
    def __init__(self, task: Task, parent=None) -> None:
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("任务提醒")
        self.setModal(False)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.resize(560, 170)
        self.setMinimumWidth(520)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(0)

        card = CardWidget(self)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(14)
        root.addWidget(card)

        icon = QLabel("!")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(38, 38)
        icon.setObjectName("reminderIcon")
        card_layout.addWidget(icon, 0, Qt.AlignTop)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)
        card_layout.addLayout(content_layout, 1)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title = StrongBodyLabel("任务提醒")
        title.setObjectName("dialogTitle")
        time_label = CaptionLabel(self._reminder_text())
        time_label.setObjectName("timeLabel")
        title_row.addWidget(title)
        title_row.addWidget(time_label)
        title_row.addStretch(1)
        content_layout.addLayout(title_row)

        self.task_title_label = BodyLabel(self.task.title)
        self.task_title_label.setWordWrap(False)
        self.task_title_label.setObjectName("taskTitle")
        self.task_title_label.setToolTip(self.task.title)
        content_layout.addWidget(self.task_title_label)

        note_text = self.task.note.strip() or "这项任务已经到提醒时间。"
        self.note_label = CaptionLabel(note_text)
        self.note_label.setWordWrap(False)
        self.note_label.setObjectName("taskNote")
        self.note_label.setToolTip(note_text)
        content_layout.addWidget(self.note_label)

        ok_button = PrimaryPushButton("知道了")
        ok_button.setFixedWidth(88)
        ok_button.clicked.connect(self.accept)
        card_layout.addWidget(ok_button, 0, Qt.AlignVCenter)

        self.setStyleSheet(
            """
            QDialog {
                background: #f8fafc;
            }
            QLabel#reminderIcon {
                background: #dbeafe;
                color: #1d4ed8;
                border-radius: 19px;
                font-size: 20px;
                font-weight: 700;
            }
            QLabel#dialogTitle {
                color: #0f172a;
                font-size: 17px;
                font-weight: 700;
            }
            QLabel#timeLabel {
                color: #64748b;
                font-size: 12px;
            }
            QLabel#taskTitle {
                color: #0f172a;
                font-size: 15px;
                font-weight: 600;
            }
            QLabel#taskNote {
                color: #64748b;
                font-size: 12px;
            }
            """
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._elide_texts()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._elide_texts()

    def _elide_texts(self) -> None:
        available_width = max(120, self.width() - 180)
        title_metrics = QFontMetrics(self.task_title_label.font())
        note_metrics = QFontMetrics(self.note_label.font())
        self.task_title_label.setText(
            title_metrics.elidedText(self.task.title, Qt.ElideRight, available_width)
        )
        note_text = self.task.note.strip() or "这项任务已经到提醒时间。"
        self.note_label.setText(note_metrics.elidedText(note_text, Qt.ElideRight, available_width))

    def _reminder_text(self) -> str:
        if self.task.repeat_type == RepeatType.WEEKDAYS:
            return f"工作日 {self.task.reminder_at.strftime('%H:%M:%S')}"
        return self.task.reminder_at.strftime("%Y-%m-%d %H:%M:%S")
