import sys
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TextIO

from src.contracts.tasks import Task
from src.sources.repository import register_source

@dataclass(frozen=True)
class StdinLineSource:
    """
    источник задач из стандартного ввода
    например, task1: hello
    """
    stream: TextIO = sys.stdin
    name: str = "stdin"

    def fetch(self) -> Iterable[Task]:
        """читает задачи из потока ввода по строкам"""
        for line_no, line in enumerate(self.stream, start=1):
            line = line.strip()
            if not line:
                continue
            parts = line.split(":", 1)
            task_id = parts[0].strip()
            payload = parts[1].strip() if len(parts) > 1 else ""
            yield Task(id=task_id, payload=payload)

@register_source("stdin")
def create_stdin_source() -> StdinLineSource:
    return StdinLineSource()