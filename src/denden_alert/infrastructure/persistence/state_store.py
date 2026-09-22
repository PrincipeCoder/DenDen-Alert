import time
import logging

logger = logging.getLogger("denden_alert.state_store")

class StateStore:
    def __init__(self, ttl_seconds: int = 86400):
        # ttl_seconds por defecto 24 horas
        self.ttl_seconds = ttl_seconds
        # dict para almacenar { 'chat_id_msg_id': timestamp }
        self._processed: dict[str, float] = {}

    def is_processed(self, alert_id: str) -> bool:
        """Verifica si un ID de alerta ya fue procesado."""
        self._cleanup()
        return alert_id in self._processed

    def mark_as_processed(self, alert_id: str) -> None:
        """Marca un ID de alerta como procesado."""
        self._processed[alert_id] = time.time()
        logger.debug(f"Mensaje {alert_id} marcado como procesado.")

    def _cleanup(self) -> None:
        """Limpia los IDs que ya han expirado su TTL."""
        current_time = time.time()
        expired_keys = [
            k for k, timestamp in self._processed.items()
            if current_time - timestamp > self.ttl_seconds
        ]
        for k in expired_keys:
            del self._processed[k]
        
        if expired_keys:
            logger.debug(f"Limpiados {len(expired_keys)} IDs de la caché de deduplicación.")
