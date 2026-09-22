import logging
import sys
import os

def setup_logging(level: int = logging.INFO) -> None:
    """Configura el sistema de logging para consola y archivo."""
    # Crear directorio logs si no existe
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger("denden_alert")
    logger.setLevel(level)

    # Evitar agregar handlers múltiples si se llama varias veces
    if logger.hasHandlers():
        return

    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler("logs/denden.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Telethon puede ser muy ruidoso, silenciarlo un poco
    logging.getLogger("telethon").setLevel(logging.WARNING)
