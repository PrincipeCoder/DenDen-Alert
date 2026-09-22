import logging
import asyncio
from denden_alert.application.ports.audio_player import AudioPlayerPort

logger = logging.getLogger("denden_alert.audio")

class LocalAudioPlayer(AudioPlayerPort):
    def __init__(self, output_device: str = "default"):
        self.output_device = output_device

    async def play(self, audio: bytes) -> None:
        """Reproduce audio en bytes. 
        Para Phase 3, pyttsx3 maneja el audio directo, así que esto es un placeholder.
        En el futuro, se puede usar pygame o simpleaudio aquí.
        """
        logger.info(f"Reproduciendo stream de audio ({len(audio)} bytes)...")
        # Placeholder para integración futura de audio en bytes
        await asyncio.sleep(1) # Simular reproducción
