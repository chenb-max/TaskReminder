from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCalendarWidget,
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import PrimaryPushButton, PushButton, StrongBodyLabel


DISPLAY_FORMAT = "%Y-%m-%d %H:%M:%S"


class DateTimePicker(PushButton):
    def __init__(self, value: datetime | None = None, parent=None) -> None:
        super().__init__(parent)
        self._value = value or datetime.now()
        self.setObjectName("dateTimePicker")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(34)
        self.clicked.connect(self._open_dialog)
        self._update_text()
        self.setStyleSheet(
            """
            QPushButton#dateTimePicker {
                text-align: left;
                padding-left: 12px;
                padding-right: 12px;
                color: #0f172a;
                background: #ffffff;
                border: 1px solid #d9e0ea;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton#dateTimePicker:hover {
                background: #f8fafc;
                border-color: #bfdbfe;
            }
            """
        )

    def date_time(self) -> datetime:
        return self._value

    def set_date_time(self, value: datetime) -> None:
        self._value = value
        self._update_text()

    def _open_dialog(self) -> None:
        dialog = DateTimeDialog(self._value, self)
        if dialog.exec() == QDialog.Accepted:
            self.set_date_time(dialog.selected_date_time())

    def _update_text(self) -> None:
        self.setText(self._value.strftime(DISPLAY_FORMAT))


class TwoDigitSpinBox(QSpinBox):
    def textFromValue(self, value: int) -> str:
        return f"{value:02d}"

    def lineEdit(self) -> QLineEdit:
        return super().lineEdit()


class DateTimeDialog(QDialog):
    def __init__(self, value: datetime, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("选择提醒时间")
        self.setModal(True)
        self.resize(420, 390)
        self._build_ui(value)

    def selected_date_time(self) -> datetime:
        date = self.calendar.selectedDate().toPython()
        return datetime(
            date.year,
            date.month,
            date.day,
            self.hour_spin.value(),
            self.minute_spin.value(),
            self.second_spin.value(),
        )

    def _build_ui(self, value: datetime) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(value.date())
        layout.addWidget(self.calendar)

        time_layout = QHBoxLayout()
        time_layout.setSpacing(8)

        self.hour_spin = self._create_spin_box(0, 23, value.hour)
        self.minute_spin = self._create_spin_box(0, 59, value.minute)
        self.second_spin = self._create_spin_box(0, 59, value.second)

        time_layout.addWidget(self._time_field("时", self.hour_spin))
        time_layout.addWidget(self._time_field("分", self.minute_spin))
        time_layout.addWidget(self._time_field("秒", self.second_spin))
        layout.addLayout(time_layout)

        quick_layout = QHBoxLayout()
        now_button = PushButton("当前时间")
        now_button.clicked.connect(self._set_now)
        quick_layout.addStretch(1)
        quick_layout.addWidget(now_button)
        layout.addLayout(quick_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        cancel_button = PushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        ok_button = PrimaryPushButton("确定")
        ok_button.setObjectName("dateTimeOkButton")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        self.setStyleSheet(
            """
            QDialog {
                background: #f8fafc;
            }
            QCalendarWidget {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
            QLabel {
                color: #475569;
            }
            QPushButton {
                color: #0f172a;
            }
            QPushButton#dateTimeOkButton {
                color: #ffffff;
            }
            QWidget#timeField {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
            }
            QSpinBox {
                background: transparent;
                border: none;
                color: #0f172a;
                font-size: 15px;
                font-weight: 600;
                padding: 0;
            }
            QSpinBox::up-button, QSpinBox::down-button,
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                width: 0;
                height: 0;
                border: none;
                background: transparent;
            }
            QPushButton#timeStepButton {
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
                border: 1px solid #dbe3ef;
                border-radius: 4px;
                background: #f8fafc;
                color: #2563eb;
                font-size: 14px;
                font-weight: 700;
                padding: 0;
            }
            QPushButton#timeStepButton:hover {
                background: #eff6ff;
                border-color: #bfdbfe;
            }
            """
        )

    def _time_field(self, label: str, spin_box: QSpinBox) -> QWidget:
        field = QWidget()
        field.setObjectName("timeField")
        field.setFixedHeight(38)

        layout = QHBoxLayout(field)
        layout.setContentsMargins(8, 3, 8, 3)
        layout.setSpacing(6)

        title = StrongBodyLabel(label)
        title.setFixedWidth(18)
        layout.addWidget(title)

        minus_button = PushButton("-")
        minus_button.setObjectName("timeStepButton")
        minus_button.clicked.connect(spin_box.stepDown)
        layout.addWidget(minus_button)

        layout.addWidget(spin_box, 1)

        plus_button = PushButton("+")
        plus_button.setObjectName("timeStepButton")
        plus_button.clicked.connect(spin_box.stepUp)
        layout.addWidget(plus_button)
        return field

    def _create_spin_box(self, minimum: int, maximum: int, value: int) -> QSpinBox:
        spin_box = TwoDigitSpinBox()
        spin_box.setRange(minimum, maximum)
        spin_box.setValue(value)
        spin_box.setWrapping(True)
        spin_box.setButtonSymbols(QSpinBox.UpDownArrows)
        spin_box.setKeyboardTracking(False)
        spin_box.setDisplayIntegerBase(10)
        spin_box.lineEdit().setAlignment(Qt.AlignCenter)
        spin_box.setFixedWidth(42)
        return spin_box

    def _set_now(self) -> None:
        now = datetime.now()
        self.calendar.setSelectedDate(now.date())
        self.hour_spin.setValue(now.hour)
        self.minute_spin.setValue(now.minute)
        self.second_spin.setValue(now.second)
