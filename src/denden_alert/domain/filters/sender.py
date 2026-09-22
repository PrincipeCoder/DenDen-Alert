from typing import List
from denden_alert.domain.models.message import Message
from .base import MessageFilter

class SenderFilter(MessageFilter):
    def __init__(self, allowed_users: List[str]):
        self.allowed_users = allowed_users

    def matches(self, message: Message) -> bool:
        if not self.allowed_users:
            return True
            
        if message.username and message.username in self.allowed_users:
            return True
        if str(message.sender_id) in self.allowed_users:
            return True
            
        return False
