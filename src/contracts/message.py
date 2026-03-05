import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Message:
    id: str
    title: str
    author: str
    message: str
