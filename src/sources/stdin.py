import sys
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TextIO

from src.contracts.tasks import Task
from src.sources.repository import register_source


def extract_messages(lines: list[str], line_no: int) -> tuple[str, str, str, str]:
    try:
        return lines[0], lines[1], lines[2], lines[3]
    except IndexError:
        raise ValueError(
            f"Line: {line_no}. Task must contain at least 4 items, separated by ':' "
        )


@dataclass(frozen=True)
class StdinLineSource:
    stream: TextIO = sys.stdin
    name: str = "stdin"

    def fetch(self) -> Iterable[Task]:
        for line_no, line in enumerate(self.stream, start=1):
            lines = line.split(":")
            if not line.strip():
                continue
            parts = line.split(":")
            if len(parts) < 1:
                continue
            task_id = parts[0]
            payload = ":".join(parts[1:])
            yield Task(id=task_id, payload=payload)

@register_source("stdin")
def create_source() -> StdinLineSource:
    return StdinLineSource()