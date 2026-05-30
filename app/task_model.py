from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from uuid import uuid4


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class TaskStatus(str, Enum):
    PENDING = "pending"
    DONE = "done"

    @property
    def label(self) -> str:
        return {
            TaskStatus.PENDING: "待提醒",
            TaskStatus.DONE: "已完成",
        }[self]


class RepeatType(str, Enum):
    ONCE = "once"
    WEEKDAYS = "weekdays"

    @property
    def label(self) -> str:
        return {
            RepeatType.ONCE: "一次性",
            RepeatType.WEEKDAYS: "工作日",
        }[self]


@dataclass(slots=True)
class Task:
    title: str
    reminder_at: datetime
    note: str = ""
    status: TaskStatus = TaskStatus.PENDING
    reminded: bool = False
    repeat_type: RepeatType = RepeatType.ONCE
    last_reminded_date: date | None = None
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_due(self) -> bool:
        if self.status != TaskStatus.PENDING:
            return False

        now = datetime.now()
        if self.repeat_type == RepeatType.WEEKDAYS:
            return (
                now.weekday() < 5
                and self.last_reminded_date != now.date()
                and (now.hour, now.minute, now.second)
                >= (self.reminder_at.hour, self.reminder_at.minute, self.reminder_at.second)
            )

        return not self.reminded and self.reminder_at <= now

    def mark_done(self) -> None:
        self.status = TaskStatus.DONE

    def mark_reminded(self) -> None:
        if self.repeat_type == RepeatType.WEEKDAYS:
            self.last_reminded_date = datetime.now().date()
            return
        self.reminded = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "note": self.note,
            "reminder_at": self.reminder_at.strftime(DATETIME_FORMAT),
            "status": self.status.value,
            "reminded": self.reminded,
            "repeat_type": self.repeat_type.value,
            "last_reminded_date": _format_date(self.last_reminded_date),
            "created_at": self.created_at.strftime(DATETIME_FORMAT),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=str(data.get("id") or uuid4().hex),
            title=str(data.get("title") or "未命名任务"),
            note=str(data.get("note") or ""),
            reminder_at=_parse_datetime(data.get("reminder_at")),
            status=_parse_status(data.get("status")),
            reminded=bool(data.get("reminded", False)),
            repeat_type=_parse_repeat_type(data.get("repeat_type")),
            last_reminded_date=_parse_date(data.get("last_reminded_date")),
            created_at=_parse_datetime(data.get("created_at")),
        )


def _parse_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, DATETIME_FORMAT)
        except ValueError:
            pass
    return datetime.now()


def _parse_status(value: object) -> TaskStatus:
    try:
        return TaskStatus(str(value))
    except ValueError:
        return TaskStatus.PENDING


def _parse_repeat_type(value: object) -> RepeatType:
    try:
        return RepeatType(str(value))
    except ValueError:
        return RepeatType.ONCE


def _parse_date(value: object) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        try:
            return datetime.strptime(value, DATE_FORMAT).date()
        except ValueError:
            return None
    return None


def _format_date(value: date | None) -> str | None:
    if value is None:
        return None
    return value.strftime(DATE_FORMAT)
