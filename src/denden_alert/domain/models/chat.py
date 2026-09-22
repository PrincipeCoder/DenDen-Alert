from dataclasses import dataclass
from enum import Enum

class ChatType(Enum):
    PRIVATE = "private"
    GROUP = "group"
    CHANNEL = "channel"
    UNKNOWN = "unknown"

@dataclass
class Chat:
    id: int
    title: str
    username: str | None
    type: ChatType
