from collections.abc import Sequence, Iterable

from src.contracts.message import Message
from src.contracts.message_source import MessageSource


class InboxApp:
    def __init__(self, sources: Sequence[MessageSource] = None):
        self._sources = sources or []

    def iter_messages(self) -> Iterable[Message]:
        for src in self._sources:
            if not isinstance(src, MessageSource):
                raise TypeError("Source object must be MessageSource")
            for message in src.fetch():
                yield message
