import asyncio
import logging
import time

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.bot.handlers import create_handlers
from src.config import load_config
from src.services.container import ServiceContainer

logger = logging.getLogger(__name__)


def setup_logging(config):
    """Настраивает логирование"""
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


async def main():
    """Основная функция запуска бота"""
    start_time = time.time()

    # Загружаем конфигурацию
    logger.info("Loading configuration...")
    config = load_config()
    setup_logging(config)

    # DI контейнер
    logger.info("Initializing service container...")
    container = ServiceContainer(config)
    consultation_service = container.get_consultation_service()

    # Загружаем сценарии (инициализация базы)
    logger.info("Loading scenarios...")
    consultation_service.reload_scenarios()

    # Создаем бота и диспетчер
    logger.info("Setting up bot and dispatcher...")
    bot = Bot(
        token=config.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Создаем и подключаем обработчики
    router = create_handlers(consultation_service)
    dp.include_router(router)

    total_startup_time = time.time() - start_time
    logger.info(f"Banking consultant bot started in {total_startup_time:.2f} seconds")
    logger.info("Press Ctrl+C to stop")

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
