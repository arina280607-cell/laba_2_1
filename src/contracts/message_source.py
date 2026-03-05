from collections.abc import Iterable
from typing import Protocol, runtime_checkable

from src.contracts.message import Message


@runtime_checkable
class MessageSource(Protocol):
    name: str

    def fetch(self) -> Iterable[Message]: ...
