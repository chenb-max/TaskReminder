from __future__ import annotations

import json
import os
from pathlib import Path

from app.task_model import Task


APP_DIR_NAME = "TaskReminder"
TASKS_FILE_NAME = "tasks.json"


def get_app_data_dir() -> Path:
    base_dir = os.environ.get("APPDATA")
    if base_dir:
        return Path(base_dir) / APP_DIR_NAME
    return Path.home() / f".{APP_DIR_NAME.lower()}"


class TaskStorage:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or get_app_data_dir() / TASKS_FILE_NAME

    def load(self) -> list[Task]:
        if not self.path.exists():
            return []

        try:
            raw_tasks = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        if not isinstance(raw_tasks, list):
            return []

        tasks: list[Task] = []
        for raw_task in raw_tasks:
            if isinstance(raw_task, dict):
                tasks.append(Task.from_dict(raw_task))
        return tasks

    def save(self, tasks: list[Task]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [task.to_dict() for task in tasks]
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
