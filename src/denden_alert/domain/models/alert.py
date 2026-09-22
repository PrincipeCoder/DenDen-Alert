from dataclasses import dataclass, field
from enum import IntEnum
from datetime import datetime
from .message import Message

class AlertPriority(IntEnum):
    # Valores menores tienen mayor prioridad en la cola
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

@dataclass(order=True)
class Alert:
    # priority debe ser el primer campo para que sortee por este atributo
    priority: AlertPriority
    created_at: datetime
    message: Message = field(compare=False)
    sanitized_text: str = field(compare=False)
    
    @property
    def id(self) -> str:
        return f"{self.message.chat.id}_{self.message.id}"
