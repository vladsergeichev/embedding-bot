import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    host: str = "qdrant"
    port: int = 6333
    collection_name: str = "scenarios"
    vector_size: int = 384
    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@dataclass
class BotConfig:
    token: str


@dataclass
class AppConfig:
    bot: BotConfig
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    data_file: str = "data/scenarios.json"
    log_level: str = "INFO"


def load_config() -> AppConfig:
    """Загружает конфигурацию из переменных окружения"""
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN not specified in environment variables")

    database_config = DatabaseConfig(
        host=os.getenv("QDRANT_HOST", "qdrant"),  # Используем имя сервиса в Docker
        port=int(os.getenv("QDRANT_PORT", "6333")),
        collection_name=os.getenv("QDRANT_COLLECTION", "scenarios"),
        vector_size=int(os.getenv("VECTOR_SIZE", "384")),
        model_name=os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        ),
    )

    app_config = AppConfig(
        bot=BotConfig(token=bot_token),
        database=database_config,
        data_file=os.getenv("DATA_FILE", "data/scenarios.json"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )

    return app_config
