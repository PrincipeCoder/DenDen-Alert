from typing import Protocol, Callable, Any, Awaitable

class TelegramClientPort(Protocol):
    """Puerto genérico para interactuar con Telegram."""

    async def connect(self) -> None:
        """Inicia conexión y autenticación con Telegram."""
        ...

    async def disconnect(self) -> None:
        """Cierra la conexión con Telegram."""
        ...

    async def listen(self, handler: Callable[[Any], Awaitable[None]]) -> None:
        """Escucha nuevos mensajes y delega al handler."""
        ...
