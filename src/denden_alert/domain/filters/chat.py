from typing import List
from denden_alert.domain.models.message import Message
from .base import MessageFilter

class ChatFilter(MessageFilter):
    def __init__(self, allowed_chats: List[str]):
        # Se normalizan los nombres/IDs
        self.allowed_chats = [str(c) for c in allowed_chats]

    def matches(self, message: Message) -> bool:
        if not self.allowed_chats:
            return True # Permite todos si no hay lista
            
        chat = message.chat
        chat_id_str = str(chat.id)
        
        # Coincide por ID, Título o Username
        if chat_id_str in self.allowed_chats:
            return True
        if chat.title and chat.title in self.allowed_chats:
            return True
        if chat.username and chat.username in self.allowed_chats:
            return True
            
        return False
