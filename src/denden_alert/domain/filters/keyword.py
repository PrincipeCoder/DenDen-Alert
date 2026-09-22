from typing import List
from denden_alert.domain.models.message import Message
from .base import MessageFilter

class KeywordFilter(MessageFilter):
    def __init__(self, keywords: List[str], case_sensitive: bool = False):
        self.case_sensitive = case_sensitive
        if not case_sensitive:
            self.keywords = [k.lower() for k in keywords]
        else:
            self.keywords = keywords

    def matches(self, message: Message) -> bool:
        if not self.keywords:
            return True # Si no hay keywords, pasa todo
            
        text = message.text
        if not self.case_sensitive:
            text = text.lower()
            
        for kw in self.keywords:
            if kw in text:
                return True
        return False
