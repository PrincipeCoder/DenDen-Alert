import logging
import edge_tts
import io
from denden_alert.application.ports.tts_engine import TTSEnginePort

logger = logging.getLogger("denden_alert.tts")

class EdgeTTSEngine(TTSEnginePort):
    def __init__(self, voice: str = "es-ES-AlvaroNeural", rate: float = 1.0, volume: float = 1.0):
        self.voice = voice
        # edge-tts usa strings relativas para la velocidad y volumen, ej: "+10%", "-5%"
        # rate de 1.0 = +0%
        rate_percent = int((rate - 1.0) * 100)
        self.rate_str = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
        
        vol_percent = int((volume - 1.0) * 100)
        self.volume_str = f"+{vol_percent}%" if vol_percent >= 0 else f"{vol_percent}%"

    async def synthesize(self, text: str, language: str) -> bytes | None:
        """Sintetiza el texto usando Microsoft Edge TTS (requiere internet)."""
        logger.info(f"Sintetizando (Edge TTS): '{text[:50]}...'")
        
        try:
            communicate = edge_tts.Communicate(
                text, 
                self.voice,
                rate=self.rate_str,
                volume=self.volume_str
            )
            
            audio_stream = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_stream.write(chunk["data"])
            
            return audio_stream.getvalue()
            
        except Exception as e:
            logger.error(f"Error en EdgeTTSEngine: {e}", exc_info=True)
            return None
