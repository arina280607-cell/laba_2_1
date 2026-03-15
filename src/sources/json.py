import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.contracts.tasks import Task
from src.sources.repository import register_source


def parse_json_line(line: str, path: str, line_no: int) -> dict[str, Any]:
    """парсит строку JSON"""
    try:
        return json.loads(line)
    except json.JSONDecodeError as error:
        raise ValueError(f"Bad JSON at {path}:{line_no}: {error}") from error



@dataclass(frozen=True)
class JsonlSource:
    """источник задач из файла"""
    path: Path
    name: str = "file-jsonl"

    def fetch(self) -> Iterable[Task]:
        """читает задачи из файла"""
        with self.path.open("r", encoding="utf-8") as file:
            for line_no, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                task_data = parse_json_line(line, str(self.path), line_no)
                task_id = str(task_data.get("id", f"{self.path.name}:{line_no}"))
                payload = {k: v for k, v in task_data.items() if k != "id"}#кладем данные кроме айди
                yield Task(id=task_id, payload=payload)


@register_source("file-jsonl")
def create_json_source(path: Path) -> JsonlSource:
    return JsonlSource(path=path)