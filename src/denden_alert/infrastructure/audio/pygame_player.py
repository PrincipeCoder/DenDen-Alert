import logging
import asyncio
import io
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from denden_alert.application.ports.audio_player import AudioPlayerPort

logger = logging.getLogger("denden_alert.audio")

class PygameAudioPlayer(AudioPlayerPort):
    def __init__(self, output_device: str = "default"):
        self.output_device = output_device
        # Inicializar el mixer de pygame
        try:
            pygame.mixer.init()
        except Exception as e:
            logger.error(f"Error inicializando pygame.mixer: {e}")

    async def play(self, audio: bytes) -> None:
        """Reproduce audio en formato MP3 desde bytes usando pygame."""
        if not audio:
            return
            
        logger.info(f"Reproduciendo audio ({len(audio)} bytes)...")
        
        try:
            audio_stream = io.BytesIO(audio)
            
            # Cargar y reproducir el sonido en el hilo principal
            pygame.mixer.music.load(audio_stream, 'mp3')
            pygame.mixer.music.play()
            
            # Esperar a que termine de reproducirse de forma asíncrona
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error reproduciendo audio: {e}", exc_info=True)
