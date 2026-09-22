from denden_alert.domain.models.message import Message
from .base import MessageFilter

class IgnoreBotFilter(MessageFilter):
    def matches(self, message: Message) -> bool:
        return not message.is_bot
