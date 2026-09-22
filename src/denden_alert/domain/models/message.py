from dataclasses import dataclass
from datetime import datetime
from .chat import Chat

@dataclass
class Message:
    id: int
    chat: Chat
    sender_id: int | None
    sender_name: str
    username: str | None
    text: str
    timestamp: datetime
    is_bot: bool
