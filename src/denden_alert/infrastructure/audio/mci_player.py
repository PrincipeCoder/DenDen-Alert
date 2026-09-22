import logging
import asyncio
import ctypes
import tempfile
import os
import time
from denden_alert.application.ports.audio_player import AudioPlayerPort

logger = logging.getLogger("denden_alert.audio")

class MCIAudioPlayer(AudioPlayerPort):
    def __init__(self, output_device: str = "default"):
        self.output_device = output_device

    async def play(self, audio: bytes) -> None:
        """Reproduce audio en formato MP3 desde bytes usando la API nativa de Windows (MCI)."""
        if not audio:
            return
            
        logger.info(f"Reproduciendo audio ({len(audio)} bytes) usando MCI nativo...")
        
        # MCI requiere un archivo físico
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.write(audio)
        temp_file.close()
        
        try:
            # Ejecutar la reproducción sincrónica bloqueante en un hilo
            await asyncio.to_thread(self._play_sync, temp_file.name)
        except Exception as e:
            logger.error(f"Error reproduciendo audio: {e}", exc_info=True)
        finally:
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass

    def _play_sync(self, file_path: str) -> None:
        """Reproduce un archivo usando la interfaz multimedia de Windows de forma bloqueante."""
        alias = f"mp3_{id(self)}_{int(time.time() * 1000)}"
        
        # open the file
        self._mci_send(f'open "{file_path}" type mpegvideo alias {alias}')
        # play and wait
        self._mci_send(f'play {alias} wait')
        # close
        self._mci_send(f'close {alias}')

    def _mci_send(self, command: str) -> None:
        buf = ctypes.create_unicode_buffer(255)
        error = ctypes.windll.winmm.mciSendStringW(command, buf, 254, 0)
        if error:
            logger.error(f"Error MCI {error} ejecutando: {command}")
