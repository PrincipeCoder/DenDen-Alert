from typing import List
from denden_alert.domain.models.message import Message
from .base import MessageFilter

class AndFilter(MessageFilter):
    def __init__(self, filters: List[MessageFilter]):
        self.filters = filters

    def matches(self, message: Message) -> bool:
        return all(f.matches(message) for f in self.filters)

class OrFilter(MessageFilter):
    def __init__(self, filters: List[MessageFilter]):
        self.filters = filters

    def matches(self, message: Message) -> bool:
        if not self.filters:
            return True
        return any(f.matches(message) for f in self.filters)
