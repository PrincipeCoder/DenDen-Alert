from typing import Protocol

class TTSEnginePort(Protocol):
    async def synthesize(self, text: str, language: str) -> bytes | None:
        """Sintetiza texto a voz.
        Retorna bytes del audio si genera un archivo o None si lo reproduce directamente.
        """
        ...
