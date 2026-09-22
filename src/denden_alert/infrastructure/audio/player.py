import logging
import asyncio
import platform
import subprocess
import tempfile
import os

from denden_alert.application.ports.audio_player import AudioPlayerPort

logger = logging.getLogger("denden_alert.audio")

class LocalAudioPlayer(AudioPlayerPort):
    def __init__(self, output_device: str = "default"):
        self.output_device = output_device
        self.os_name = platform.system()

    async def play(self, audio: bytes) -> None:
        """Reproduce audio WAV usando el reproductor nativo del sistema operativo."""
        if not audio:
            return
            
        logger.info(f"Reproduciendo audio ({len(audio)} bytes) en {self.os_name}...")
        
        # Guardar en archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_file.write(audio)
        temp_file.close()
        
        try:
            if self.os_name == "Windows":
                await asyncio.to_thread(self._play_windows, temp_file.name)
            else:
                await asyncio.to_thread(self._play_linux, temp_file.name)
        except Exception as e:
            logger.error(f"Error reproduciendo audio: {e}")
        finally:
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass

    def _play_windows(self, file_path: str) -> None:
        import winsound
        # Reproduce sincrónicamente (SND_SYNC) bloqueando el hilo hasta terminar
        winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_SYNC)

    def _play_linux(self, file_path: str) -> None:
        # Usa 'aplay' de ALSA
        try:
            subprocess.run(
                ["aplay", "-q", file_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            logger.error(f"aplay falló. Asegúrate de tener alsa-utils instalado y un host de audio válido.")
        except FileNotFoundError:
            logger.error("Comando 'aplay' no encontrado. Instala alsa-utils en tu distribución de Linux.")
