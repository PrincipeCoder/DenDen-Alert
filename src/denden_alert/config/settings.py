import os
from pathlib import Path
from functools import lru_cache
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field

# Modelos para config.yaml
class TelegramConfig(BaseModel):
    chats: list[str] = Field(default_factory=list)

class FiltersConfig(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    users: list[str] = Field(default_factory=list)
    case_sensitive: bool = False

class TTSConfig(BaseModel):
    provider: str = "local"
    language: str = "es"
    rate: float = 1.0
    volume: float = 1.0

class AudioConfig(BaseModel):
    output_device: str = "default"

class BehaviorConfig(BaseModel):
    read_only_new_messages: bool = True
    ignore_bots: bool = True
    ignore_empty_messages: bool = True
    deduplicate: bool = True

class YamlSettings(BaseModel):
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    filters: FiltersConfig = Field(default_factory=FiltersConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    behavior: BehaviorConfig = Field(default_factory=BehaviorConfig)

# Settings principales que combina .env y yaml
class Settings(BaseSettings):
    telegram_api_id: int
    telegram_api_hash: str
    telegram_session_name: str = "denden_alert"
    
    yaml_config_path: str = "config/config.yaml"
    
    # Cargado desde YAML
    app_config: YamlSettings = Field(default_factory=YamlSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def load_yaml(self) -> None:
        path = Path(self.yaml_config_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.app_config = YamlSettings(**data)
        else:
            print(f"Warning: Configuration file {self.yaml_config_path} not found. Using defaults.")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.load_yaml()
    return settings
