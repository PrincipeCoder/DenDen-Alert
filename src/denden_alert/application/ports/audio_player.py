from typing import Protocol

class AudioPlayerPort(Protocol):
    async def play(self, audio: bytes) -> None:
        """Reproduce un stream de audio en bytes."""
        ...
