from functools import wraps
from typing import Callable, Type

from contracts.message_source import MessageSource

SourceFactory = Callable[..., MessageSource]

REGISTRY: dict[str, SourceFactory] = {}

def register_source(name: str):
    def _decorator(class_or_function: Type | Callable):
        REGISTRY[name] = class_or_function
        return class_or_function
    return _decorator