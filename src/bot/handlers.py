import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.services.consultation_service import ConsultationService

logger = logging.getLogger(__name__)


class Handlers:
    """Класс обработчиков с внедрением зависимостей"""

    def __init__(self, consultation_service: ConsultationService):
        self.consultation_service = consultation_service
        self.router = Router()
        self._setup_handlers()

    def _setup_handlers(self):
        """Настраивает обработчики"""
        self.router.message.register(self.cmd_start, Command("start"))
        self.router.message.register(self.cmd_help, Command("help"))
        self.router.message.register(self.cmd_reload, Command("reload"))
        self.router.message.register(self.handle_text_message, F.text)
        self.router.message.register(self.handle_other_messages)

    async def cmd_start(self, message: Message):
        """Обработчик команды /start"""
        welcome_text = """
        Добро пожаловать в Банковский Консультант!

        Я помогу вам получить ответы на вопросы о банковских услугах:
        • Кредиты и займы
        • Депозиты и вклады  
        • Банковские карты
        • Переводы и платежи
        • Ипотека
        • И другие банковские услуги

        Просто напишите ваш вопрос, и я найду для вас подходящий ответ!
        """
        await message.answer(welcome_text.strip())

    async def cmd_help(self, message: Message):
        """Обработчик команды /help"""
        help_text = """
        Доступные команды:

        /start - Начать работу с ботом
        /help - Показать эту справку
        /reload - Перезагрузить базу знаний

        Как использовать:
        Просто напишите ваш вопрос о банковских услугах, например:
        • "Как оформить кредит?"
        • "Какие документы нужны для карты?"
        • "Как пополнить карту?"
        """
        await message.answer(help_text.strip())

    async def cmd_reload(self, message: Message):
        """Перезагружает базу знаний из файла"""
        try:
            scenarios_count = self.consultation_service.reload_scenarios()
            await message.answer(
                f"База знаний успешно перезагружена! Загружено {scenarios_count} сценариев."
            )
            user_id = message.from_user.id if message.from_user else "unknown"
            logger.info(f"Database reloaded by user {user_id}")

        except Exception as e:
            await message.answer(f"Ошибка при перезагрузке базы знаний: {str(e)}")
            logger.error(f"Database reload error: {e}")

    async def handle_text_message(self, message: Message):
        """Обработчик текстовых сообщений"""
        user_question = message.text.strip() if message.text else ""

        if not user_question:
            await message.answer("Пожалуйста, напишите ваш вопрос.")
            return

        try:
            similar_scenarios = self.consultation_service.find_similar_scenarios(
                user_question
            )
            response = self.consultation_service.format_response(similar_scenarios)

            await message.answer(response)
            logger.info(
                f"User {message.from_user.id if message.from_user else 'unknown'} asked: {user_question}"
            )

        except Exception as e:
            await message.answer(f"Произошла ошибка при поиске ответа: {str(e)}")
            logger.error(f"Search error: {e}")

    async def handle_other_messages(self, message: Message):
        """Обработчик всех остальных типов сообщений"""
        await message.answer(
            "Пожалуйста, отправьте текстовое сообщение с вашим вопросом."
        )


def create_handlers(consultation_service: ConsultationService) -> Router:
    """Создает и возвращает роутер с обработчиками"""
    handlers = Handlers(consultation_service)
    return handlers.router
