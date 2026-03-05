import json
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.contracts.message import Message
from src.sources.repository import register_source


def parse_json_file(line: str, path: str, line_no: int) -> dict[str, Any]:
    try:
        return json.loads(line)
    except json.JSONDecodeError as error:
        raise ValueError(f"Bad JSON at {path}:{line_no}: {error}") from error


@dataclass(frozen=True)
class JsonlSource:
    path: Path
    name: str = "file-jsonl"

    def fetch(self) -> Iterable[Message]:
        with self.path.open("r", encoding="utf-8") as file:
            for line_no, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                message = parse_json_file(line, str(self.path), line_no)
                message_id = str(message.get("id", f"{self.path.name}:{line_no}"))
                message_title = message.get("title", "")
                message_author = message.get("author", "")
                message_content = message.get("content", "")
                yield Message(
                    id=message_id, title=message_title, author=message_author, message=message_content
                )


@register_source("file-jsonl")
def create_json_source(path: Path) -> JsonlSource:
    return JsonlSource(path=path)