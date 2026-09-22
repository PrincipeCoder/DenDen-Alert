from typing import Protocol
from denden_alert.domain.models.message import Message

class MessageFilter(Protocol):
    def matches(self, message: Message) -> bool:
        ...
