import logging
from typing import Callable, Any, Awaitable
from telethon import TelegramClient, events
from denden_alert.application.ports.telegram_client import TelegramClientPort

logger = logging.getLogger("denden_alert.telegram")

class TelethonTelegramClient(TelegramClientPort):
    def __init__(self, session_name: str, api_id: int, api_hash: str, chats_to_monitor: list[str]):
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.chats_to_monitor = chats_to_monitor
        self.client = TelegramClient(session_name, api_id, api_hash)
        self._handler: Callable[[Any], Awaitable[None]] | None = None

    async def connect(self) -> None:
        logger.info("Conectando a Telegram...")
        await self.client.start()
        logger.info("Autenticación exitosa con Telegram.")

    async def disconnect(self) -> None:
        logger.info("Desconectando de Telegram...")
        await self.client.disconnect()

    async def listen(self, handler: Callable[[Any], Awaitable[None]]) -> None:
        self._handler = handler
        
        # Filtramos internamente los chats si están configurados
        target_chats = self.chats_to_monitor if self.chats_to_monitor else None
        
        @self.client.on(events.NewMessage(chats=target_chats))
        async def new_message_handler(event: events.NewMessage.Event) -> None:
            if self._handler:
                try:
                    await self._handler(event)
                except Exception as e:
                    logger.error(f"Error procesando mensaje: {e}", exc_info=True)

        logger.info(f"Escuchando mensajes en los chats: {target_chats}")
        await self.client.run_until_disconnected()
