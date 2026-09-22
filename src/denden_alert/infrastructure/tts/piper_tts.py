import logging
import asyncio
import os
import urllib.request
import tempfile
import wave
from piper import PiperVoice
from typing import Optional

from denden_alert.application.ports.tts_engine import TTSEnginePort

logger = logging.getLogger("denden_alert.tts")

class PiperTTSEngine(TTSEnginePort):
    def __init__(self, rate: float = 1.0, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.models_dir = "models"
        self.model_name = "es_ES-alba-medium.onnx"
        self.model_path = os.path.join(self.models_dir, self.model_name)
        self.config_path = self.model_path + ".json"
        
        self.voice: Optional[PiperVoice] = None

    async def initialize(self) -> None:
        """Inicializa Piper y descarga el modelo si no existe."""
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)

        if not os.path.exists(self.model_path) or not os.path.exists(self.config_path):
            await self._download_model()

        logger.info(f"Cargando modelo Piper TTS: {self.model_name}...")
        
        # Cargar el modelo de forma asíncrona para no bloquear el loop principal
        await asyncio.to_thread(self._load_voice)

    def _load_voice(self):
        self.voice = PiperVoice.load(self.model_path, config_path=self.config_path)

    async def _download_model(self):
        """Descarga el modelo de voz Alba (Español) desde HuggingFace."""
        base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/alba/medium/"
        
        logger.info(f"Descargando modelo de voz Piper TTS ({self.model_name}). Esto solo ocurre una vez...")
        
        await asyncio.to_thread(
            urllib.request.urlretrieve, 
            base_url + self.model_name, 
            self.model_path
        )
        
        logger.info(f"Descargando configuración del modelo...")
        await asyncio.to_thread(
            urllib.request.urlretrieve, 
            base_url + self.model_name + ".json", 
            self.config_path
        )
        logger.info("¡Descarga de voz completada!")

    async def synthesize(self, text: str) -> bytes:
        """Convierte el texto a audio en formato WAV (bytes)."""
        if not self.voice:
            await self.initialize()

        logger.info(f"Sintetizando (Piper): '{text[:50]}...'")
        
        # Piper escribe directamente a un archivo WAV, usaremos un archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_file.close()
        
        try:
            # Sintetizar de forma bloqueante en un hilo secundario
            await asyncio.to_thread(self._synthesize_sync, text, temp_file.name)
            
            # Leer los bytes resultantes
            with open(temp_file.name, "rb") as f:
                audio_bytes = f.read()
                
            return audio_bytes
        finally:
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass

    def _synthesize_sync(self, text: str, output_path: str):
        with wave.open(output_path, "wb") as wav_file:
            # Configuración por defecto para mono 16kHz o 22kHz que Piper requiera
            # Piper setea automáticamente los parámetros del archivo WAV en el método synthesize
            self.voice.synthesize(text, wav_file)
