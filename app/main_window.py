from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    CaptionLabel,
    CardWidget,
    CheckBox,
    LineEdit,
    PrimaryPushButton,
    PushButton,
    StrongBodyLabel,
    SubtitleLabel,
    TextEdit,
)

from app import autostart
from app.datetime_picker import DateTimePicker
from app.storage import TaskStorage
from app.task_model import RepeatType, Task, TaskStatus


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.storage = TaskStorage()
        self.tasks = self.storage.load()
        self.tray_controller = None
        self.reminder_service = None
        self.allow_quit = False
        self.editing_task_id: str | None = None

        self.setWindowTitle("TaskReminder")
        self.resize(920, 720)
        self.setMinimumSize(860, 660)
        self._build_ui()
        self.refresh_tasks()

    def set_tray_controller(self, tray_controller) -> None:
        self.tray_controller = tray_controller

    def set_reminder_service(self, reminder_service) -> None:
        self.reminder_service = reminder_service

    def show_from_tray(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def save_tasks(self) -> None:
        self.storage.save(self.tasks)

    def refresh_tasks(self) -> None:
        self.tasks.sort(key=lambda task: (task.status != TaskStatus.PENDING, task.reminder_at))
        self.table.setRowCount(len(self.tasks))

        for row, task in enumerate(self.tasks):
            self.table.setRowHeight(row, 36)
            self._set_readonly_item(row, 0, task.title)
            self._set_readonly_item(row, 1, self._reminder_text(task))
            self._set_status_badge(row, task)
            self._set_actions(row, task)

        self.empty_label.setVisible(not self.tasks)
        self.table.updateGeometry()

    def closeEvent(self, event) -> None:
        if self.allow_quit:
            event.accept()
            return

        event.ignore()
        self.hide()
        if self.tray_controller is not None:
            self.tray_controller.show_message("TaskReminder", "程序已最小化到系统托盘。")

    def _build_ui(self) -> None:
        central = QWidget(self)
        central.setObjectName("centralWidget")
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(10)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        header_layout.addWidget(SubtitleLabel("TaskReminder"))
        header_layout.addWidget(CaptionLabel("本地任务提醒、托盘常驻和开机自启"))
        root_layout.addLayout(header_layout)

        form_card = CardWidget()
        form_card_layout = QVBoxLayout(form_card)
        form_card_layout.setContentsMargins(16, 12, 16, 12)
        form_card_layout.setSpacing(10)
        form_card_layout.addWidget(StrongBodyLabel("新建提醒"))

        form_layout = QGridLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(8)
        form_layout.setColumnMinimumWidth(0, 58)
        form_layout.setColumnStretch(0, 0)
        form_layout.setColumnStretch(1, 1)

        self.title_input = LineEdit()
        self.title_input.setPlaceholderText("例如：提交周报")
        form_layout.addWidget(self._form_label("标题"), 0, 0)
        form_layout.addWidget(self.title_input, 0, 1)

        self.note_input = TextEdit()
        self.note_input.setPlaceholderText("备注可选")
        self.note_input.setFixedHeight(48)
        form_layout.addWidget(self._form_label("备注"), 1, 0, Qt.AlignTop)
        form_layout.addWidget(self.note_input, 1, 1)

        self.datetime_input = DateTimePicker(datetime.now())
        self.weekday_repeat_checkbox = CheckBox("工作日重复提醒")

        reminder_layout = QHBoxLayout()
        reminder_layout.setContentsMargins(0, 0, 0, 0)
        reminder_layout.setSpacing(16)
        self.datetime_input.setFixedWidth(390)
        reminder_layout.addWidget(self.datetime_input, 0)
        reminder_layout.addWidget(self.weekday_repeat_checkbox, 0, Qt.AlignVCenter)
        reminder_layout.addStretch(1)
        form_layout.addWidget(self._form_label("时间"), 2, 0)
        form_layout.addLayout(reminder_layout, 2, 1)

        self.add_button = PrimaryPushButton("添加任务")
        self.add_button.clicked.connect(self.add_task)
        self.add_button.setFixedHeight(32)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        button_layout.addWidget(self.add_button, 1)

        self.cancel_edit_button = PushButton("取消修改")
        self.cancel_edit_button.setFixedHeight(32)
        self.cancel_edit_button.hide()
        self.cancel_edit_button.clicked.connect(self.cancel_edit)
        button_layout.addWidget(self.cancel_edit_button, 0)
        form_layout.addLayout(button_layout, 3, 1)
        form_card_layout.addLayout(form_layout)
        root_layout.addWidget(form_card, 0)

        settings_card = CardWidget()
        settings_card.setMaximumHeight(58)
        settings_layout_outer = QVBoxLayout(settings_card)
        settings_layout_outer.setContentsMargins(16, 10, 16, 10)
        settings_layout_outer.setSpacing(6)
        settings_layout = QHBoxLayout()
        self.autostart_checkbox = CheckBox("开机自启")
        self.autostart_checkbox.setEnabled(autostart.is_supported())
        self.autostart_checkbox.setChecked(autostart.is_enabled())
        self.autostart_checkbox.toggled.connect(self.toggle_autostart)
        settings_layout.addWidget(self.autostart_checkbox)
        settings_layout.addStretch(1)
        settings_layout_outer.addLayout(settings_layout)
        root_layout.addWidget(settings_card, 0)

        list_card = CardWidget()
        list_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        list_card.setMinimumHeight(380)
        list_layout = QVBoxLayout(list_card)
        list_layout.setContentsMargins(16, 12, 16, 14)
        list_layout.setSpacing(8)

        list_header = QHBoxLayout()
        list_header.addWidget(StrongBodyLabel("任务列表"))
        list_header.addStretch(1)
        self.empty_label = CaptionLabel("暂无任务")
        self.empty_label.setAlignment(Qt.AlignCenter)
        list_header.addWidget(self.empty_label)
        list_layout.addLayout(list_header)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(["标题", "提醒时间", "状态", "操作"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setMinimumHeight(330)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(3, 154)
        self.table.setAlternatingRowColors(False)
        list_layout.addWidget(self.table, 1)
        root_layout.addWidget(list_card, 1)
        root_layout.setStretchFactor(form_card, 0)
        root_layout.setStretchFactor(settings_card, 0)
        root_layout.setStretchFactor(list_card, 1)

        self.setCentralWidget(central)
        self.setStyleSheet(
            """
            QWidget#centralWidget {
                background: #f8fafc;
            }
            QLabel#formLabel {
                color: #0f172a;
                font-size: 12px;
            }
            LineEdit, TextEdit {
                color: #0f172a;
                background: #ffffff;
            }
            QTableWidget {
                background: white;
                color: #0f172a;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                gridline-color: #eef2f7;
                selection-background-color: #e8f1ff;
                selection-color: #0f172a;
            }
            QTableWidget::viewport {
                background: white;
            }
            QHeaderView::section {
                background: #f1f5f9;
                color: #334155;
                border: none;
                padding: 6px;
                font-weight: 600;
            }
            QTableCornerButton::section {
                background: #f1f5f9;
                border: none;
            }
            QTableWidget::item {
                color: #0f172a;
                padding: 4px 6px;
            }
            QTableWidget::item:selected {
                background: #e8f1ff;
                color: #0f172a;
            }
            QPushButton#tableActionButton {
                min-width: 42px;
                max-width: 42px;
                min-height: 22px;
                max-height: 22px;
                border: 1px solid #d9e0ea;
                border-radius: 4px;
                background: #ffffff;
                color: #0f172a;
                padding: 0;
                font-size: 12px;
            }
            QPushButton#tableActionButton:hover {
                background: #f1f5f9;
                border-color: #cbd5e1;
            }
            QPushButton#tableActionButton:disabled {
                color: #94a3b8;
                background: #f8fafc;
                border-color: #e5e7eb;
            }
            """
        )

    def add_task(self) -> None:
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "无法添加任务", "请输入任务标题。")
            return

        if self.editing_task_id is not None:
            self.save_edited_task(title)
            return

        task = Task(
            title=title,
            note=self.note_input.toPlainText().strip(),
            reminder_at=self.datetime_input.date_time(),
            repeat_type=RepeatType.WEEKDAYS if self.weekday_repeat_checkbox.isChecked() else RepeatType.ONCE,
        )
        self.tasks.append(task)
        self.save_tasks()
        self.refresh_tasks()
        self.reset_form()

    def save_edited_task(self, title: str) -> None:
        task = self._find_task(self.editing_task_id or "")
        if task is None:
            self.reset_form()
            return

        task.title = title
        task.note = self.note_input.toPlainText().strip()
        task.reminder_at = self.datetime_input.date_time()
        task.repeat_type = RepeatType.WEEKDAYS if self.weekday_repeat_checkbox.isChecked() else RepeatType.ONCE
        task.status = TaskStatus.PENDING
        task.reminded = False
        task.last_reminded_date = None

        self.save_tasks()
        self.refresh_tasks()
        self.reset_form()

    def reset_form(self) -> None:
        self.editing_task_id = None
        self.title_input.clear()
        self.note_input.clear()
        self.weekday_repeat_checkbox.setChecked(False)
        self.datetime_input.set_date_time(datetime.now())
        self.add_button.setText("添加任务")
        self.cancel_edit_button.hide()

    def cancel_edit(self) -> None:
        self.reset_form()

    def toggle_autostart(self, enabled: bool) -> None:
        try:
            autostart.set_enabled(enabled)
        except Exception as exc:
            self.autostart_checkbox.blockSignals(True)
            self.autostart_checkbox.setChecked(not enabled)
            self.autostart_checkbox.blockSignals(False)
            QMessageBox.warning(self, "开机自启设置失败", str(exc))

    def mark_done(self, task_id: str) -> None:
        task = self._find_task(task_id)
        if task is None:
            return
        task.mark_done()
        self.save_tasks()
        self.refresh_tasks()

    def _reminder_text(self, task: Task) -> str:
        if task.repeat_type == RepeatType.WEEKDAYS:
            return f"工作日 {task.reminder_at.strftime('%H:%M:%S')}"
        return task.reminder_at.strftime("%Y-%m-%d %H:%M:%S")

    def delete_task(self, task_id: str) -> None:
        self.tasks = [task for task in self.tasks if task.id != task_id]
        if self.editing_task_id == task_id:
            self.reset_form()
        self.save_tasks()
        self.refresh_tasks()

    def edit_task(self, task_id: str) -> None:
        task = self._find_task(task_id)
        if task is None:
            return

        self.editing_task_id = task.id
        self.title_input.setText(task.title)
        self.note_input.setPlainText(task.note)
        self.datetime_input.set_date_time(task.reminder_at)
        self.weekday_repeat_checkbox.setChecked(task.repeat_type == RepeatType.WEEKDAYS)
        self.add_button.setText("保存修改")
        self.cancel_edit_button.show()
        self.title_input.setFocus()

    def _find_task(self, task_id: str) -> Task | None:
        return next((task for task in self.tasks if task.id == task_id), None)

    def _set_readonly_item(self, row: int, column: int, text: str) -> None:
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, column, item)

    def _set_status_badge(self, row: int, task: Task) -> None:
        if task.status == TaskStatus.DONE:
            text = "已完成"
            color = "#16a34a"
        elif task.repeat_type == RepeatType.WEEKDAYS:
            text = "工作日"
            color = "#7c3aed"
        elif task.reminded:
            text = "已提醒"
            color = "#2563eb"
        else:
            text = "待提醒"
            color = "#b45309"

        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        item.setTextAlignment(Qt.AlignCenter)
        item.setForeground(QBrush(QColor(color)))
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        self.table.setItem(row, 2, item)

    def _set_actions(self, row: int, task: Task) -> None:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(3, 0, 3, 0)
        layout.setSpacing(4)

        edit_button = QPushButton("编辑")
        edit_button.setObjectName("tableActionButton")
        edit_button.setFixedSize(42, 22)
        edit_button.clicked.connect(lambda _checked=False, task_id=task.id: self.edit_task(task_id))
        layout.addWidget(edit_button)

        done_button = QPushButton("完成")
        done_button.setObjectName("tableActionButton")
        done_button.setFixedSize(42, 22)
        done_button.setEnabled(task.status != TaskStatus.DONE and task.repeat_type != RepeatType.WEEKDAYS)
        if task.repeat_type == RepeatType.WEEKDAYS:
            done_button.setToolTip("工作日重复任务不会自动完成，可删除停止提醒。")
        done_button.clicked.connect(lambda _checked=False, task_id=task.id: self.mark_done(task_id))
        layout.addWidget(done_button)

        delete_button = QPushButton("删除")
        delete_button.setObjectName("tableActionButton")
        delete_button.setFixedSize(42, 22)
        delete_button.clicked.connect(lambda _checked=False, task_id=task.id: self.delete_task(task_id))
        layout.addWidget(delete_button)

        self.table.setCellWidget(row, 3, widget)

    def _form_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setFixedWidth(58)
        label.setObjectName("formLabel")
        return label
