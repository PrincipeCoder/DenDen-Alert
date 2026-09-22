import logging
from denden_alert.domain.models.message import Message
from denden_alert.domain.models.alert import Alert, AlertPriority
from denden_alert.domain.filters import MessageFilter
from denden_alert.application.services.text_sanitizer import TextSanitizer
from denden_alert.infrastructure.persistence.state_store import StateStore

logger = logging.getLogger("denden_alert.processor")

class MessageProcessor:
    def __init__(self, filter_engine: MessageFilter, sanitizer: TextSanitizer, state_store: StateStore | None = None):
        self.filter_engine = filter_engine
        self.sanitizer = sanitizer
        self.state_store = state_store

    def process(self, message: Message) -> Alert | None:
        """Procesa un mensaje y retorna una Alerta si pasa los filtros y no está duplicado."""
        alert_id = f"{message.chat.id}_{message.id}"
        
        if self.state_store and self.state_store.is_processed(alert_id):
            logger.debug(f"Mensaje {alert_id} ignorado (duplicado).")
            return None
            
        if not self.filter_engine.matches(message):
            logger.debug(f"Mensaje {alert_id} ignorado por los filtros.")
            return None
            
        sanitized = self.sanitizer.sanitize(message.text)
        if not sanitized:
            logger.debug(f"Mensaje {alert_id} ignorado (texto vacío tras sanitizar).")
            return None
            
        alert = Alert(
            priority=AlertPriority.NORMAL,
            created_at=message.timestamp,
            message=message,
            sanitized_text=sanitized
        )
        
        if self.state_store:
            self.state_store.mark_as_processed(alert_id)
        
        logger.info(f"¡Alerta generada para el mensaje {alert_id} del chat {message.chat.title}!")
        return alert
