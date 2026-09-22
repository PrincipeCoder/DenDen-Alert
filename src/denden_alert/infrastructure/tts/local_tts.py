import logging
import asyncio
import pyttsx3
from denden_alert.application.ports.tts_engine import TTSEnginePort

logger = logging.getLogger("denden_alert.tts")

class LocalTTSEngine(TTSEnginePort):
    def __init__(self, rate: float = 1.0, volume: float = 1.0):
        self.rate_multiplier = rate
        self.volume = volume

    async def synthesize(self, text: str, language: str) -> bytes | None:
        """Sintetiza y reproduce el texto usando pyttsx3."""
        logger.info(f"Reproduciendo: '{text}'")
        
        # Ejecutamos pyttsx3 en un thread separado para no bloquear el loop asíncrono
        await asyncio.to_thread(self._speak, text)
        return None

    def _speak(self, text: str) -> None:
        try:
            engine = pyttsx3.init()
            
            # Ajustar configuración
            rate = engine.getProperty('rate')
            engine.setProperty('rate', int(rate * self.rate_multiplier))
            engine.setProperty('volume', self.volume)
            
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"Error en LocalTTSEngine: {e}")
