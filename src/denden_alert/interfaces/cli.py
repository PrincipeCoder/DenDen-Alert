import argparse
import asyncio
import logging
from telethon import events

from denden_alert.config import get_settings
from denden_alert.interfaces.logging import setup_logging
from denden_alert.infrastructure.telegram.telethon_client import TelethonTelegramClient
from denden_alert.infrastructure.tts.local_tts import LocalTTSEngine
from denden_alert.infrastructure.audio.player import LocalAudioPlayer

from denden_alert.domain.filters import (
    KeywordFilter, ChatFilter, IgnoreBotFilter, SenderFilter, AndFilter
)
from denden_alert.application.services import TextSanitizer, MessageProcessor
from denden_alert.application.services.alert_service import AlertService
from denden_alert.infrastructure.tts.piper_tts import PiperTTSEngine
from denden_alert.infrastructure.audio.player import LocalAudioPlayer
from denden_alert.infrastructure.persistence.state_store import StateStore
from denden_alert.domain.models.chat import Chat, ChatType
from denden_alert.domain.models.message import Message

logger = logging.getLogger("denden_alert.cli")

def build_dependencies(settings):
    # 1. Configurar Filtros
    bot_filter = IgnoreBotFilter() if settings.app_config.behavior.ignore_bots else None
    
    chat_filter = ChatFilter(settings.app_config.telegram.chats) if settings.app_config.telegram.chats else None
    
    keyword_filter = KeywordFilter(
        settings.app_config.filters.keywords, 
        case_sensitive=settings.app_config.filters.case_sensitive
    ) if settings.app_config.filters.keywords else None
    
    sender_filter = SenderFilter(settings.app_config.filters.users) if settings.app_config.filters.users else None
    
    active_filters = []
    if bot_filter: active_filters.append(bot_filter)
    if chat_filter: active_filters.append(chat_filter)
    if keyword_filter: active_filters.append(keyword_filter)
    if sender_filter: active_filters.append(sender_filter)
    
    composite_filter = AndFilter(active_filters)
    
    # 2. Configurar Servicios
    state_store = StateStore() if settings.app_config.behavior.deduplicate else None
    sanitizer = TextSanitizer()
    processor = MessageProcessor(composite_filter, sanitizer, state_store=state_store)
    
    tts_engine = PiperTTSEngine(
        rate=settings.app_config.tts.rate, 
        volume=settings.app_config.tts.volume
    )
    audio_player = LocalAudioPlayer(output_device=settings.app_config.audio.output_device)
    
    alert_service = AlertService(tts_engine, audio_player)
    
    return processor, alert_service

async def _map_event_to_message(event: events.NewMessage.Event) -> Message:
    t_chat = await event.get_chat()
    sender = await event.get_sender()
    
    chat_title = getattr(t_chat, 'title', 'Private Chat')
    chat_username = getattr(t_chat, 'username', None)
    chat_type = ChatType.GROUP # Simplificación por ahora
    
    sender_name = getattr(sender, 'username', getattr(sender, 'first_name', 'Unknown'))
    is_bot = getattr(sender, 'bot', False)
    
    chat = Chat(id=event.chat_id, title=chat_title, username=chat_username, type=chat_type)
    
    return Message(
        id=event.id,
        chat=chat,
        sender_id=event.sender_id,
        sender_name=sender_name,
        username=getattr(sender, 'username', None),
        text=event.raw_text,
        timestamp=event.date,
        is_bot=is_bot
    )

async def start_app() -> None:
    settings = get_settings()
    
    print("╔══════════════════════════════════╗")
    print("║          DenDen-Alert            ║")
    print("║     Telegram Voice Alert System  ║")
    print("╚══════════════════════════════════╝\n")

    logger.info("Iniciando DenDen-Alert...")
    
    processor, alert_service = build_dependencies(settings)
    alert_service.start()

    client = TelethonTelegramClient(
        session_name=settings.telegram_session_name,
        api_id=settings.telegram_api_id,
        api_hash=settings.telegram_api_hash,
        chats_to_monitor=None # Ahora filtramos a nivel de dominio
    )
    
    async def _message_handler(event: events.NewMessage.Event) -> None:
        try:
            msg = await _map_event_to_message(event)
            alert = processor.process(msg)
            if alert:
                await alert_service.enqueue_alert(alert)
        except Exception as e:
            logger.error(f"Error en el handler de mensajes: {e}", exc_info=True)

    try:
        await client.connect()
        logger.info("DenDen-Alert está en ejecución. Presiona Ctrl+C para salir.")
        await client.listen(_message_handler)
    except KeyboardInterrupt:
        logger.info("Señal de interrupción recibida.")
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
    finally:
        alert_service.stop()
        await client.disconnect()
        logger.info("DenDen-Alert detenido.")

def main() -> None:
    parser = argparse.ArgumentParser(description="DenDen-Alert CLI")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    start_parser = subparsers.add_parser("start", help="Inicia el servicio de DenDen-Alert")
    args = parser.parse_args()
    
    setup_logging()

    if args.command == "start":
        try:
            asyncio.run(start_app())
        except KeyboardInterrupt:
            pass
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
