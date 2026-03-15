from collections.abc import Iterable
from typing import Protocol, runtime_checkable

from src.contracts.tasks import Task


@runtime_checkable
class TaskSource(Protocol):
    """
    протокол, определяющий контракт источника задач
    поле name - идентификатор источника
    метод fetch(self) - получение задач
    """
    name: str
    def fetch(self) -> Iterable[Task]: ...
