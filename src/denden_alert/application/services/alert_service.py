import logging
import asyncio
from denden_alert.domain.models.alert import Alert
from denden_alert.application.ports.tts_engine import TTSEnginePort
from denden_alert.application.ports.audio_player import AudioPlayerPort

logger = logging.getLogger("denden_alert.alert_service")

class AlertService:
    def __init__(self, tts_engine: TTSEnginePort, audio_player: AudioPlayerPort | None = None):
        self.tts_engine = tts_engine
        self.audio_player = audio_player
        self.queue: asyncio.PriorityQueue[Alert] = asyncio.PriorityQueue()
        self._worker_task: asyncio.Task | None = None

    def start(self) -> None:
        """Inicia el worker que procesa las alertas en cola."""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._process_queue())
            logger.debug("AlertService worker iniciado.")

    def stop(self) -> None:
        """Detiene el worker."""
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            logger.debug("AlertService worker detenido.")

    async def enqueue_alert(self, alert: Alert) -> None:
        """Encola una alerta para ser reproducida."""
        await self.queue.put(alert)
        logger.debug(f"Alerta {alert.id} encolada. Tamaño de cola: {self.queue.qsize()}")

    async def _process_queue(self) -> None:
        while True:
            try:
                alert = await self.queue.get()
                logger.info(f"Procesando alerta: {alert.sanitized_text[:50]}...")
                
                audio_data = await self.tts_engine.synthesize(alert.sanitized_text, "es")
                
                # Si el motor TTS retorna bytes (ej. Azure/ElevenLabs), lo reproducimos
                if audio_data and self.audio_player:
                    await self.audio_player.play(audio_data)
                    
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error procesando alerta: {e}", exc_info=True)
                # Asegurar que la tarea no quede bloqueada
                if hasattr(self, 'queue') and not self.queue.empty():
                    self.queue.task_done()
