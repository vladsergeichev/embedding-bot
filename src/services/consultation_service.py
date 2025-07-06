import json
import logging
import time
from typing import List, Tuple

from src.database.base import VectorDatabase

logger = logging.getLogger(__name__)


class ConsultationService:
    """Сервис для работы с консультациями"""

    def __init__(
        self, database: VectorDatabase, data_file: str = "data/scenarios.json"
    ):
        self.database = database
        self.data_file = data_file

    def reload_scenarios(self) -> int:
        """Перезагружает сценарии из файла"""
        try:
            logger.info("Starting scenarios reload...")
            start_time = time.time()

            scenarios = self._load_scenarios_from_file()
            if not scenarios:
                logger.warning("No scenarios loaded from file")
                return 0

            logger.info(f"Loaded {len(scenarios)} scenarios from file")

            # Очищаем и добавляем сценарии
            logger.info("Clearing existing scenarios...")
            self.database.clear_scenarios()

            self.database.add_scenarios(scenarios)

            total_time = time.time() - start_time
            logger.info(
                f"Successfully reloaded {len(scenarios)} scenarios in {total_time:.2f} seconds"
            )
            return len(scenarios)

        except Exception as e:
            logger.error(f"Failed to reload scenarios: {e}")
            raise

    def _load_scenarios_from_file(self) -> List[dict]:
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                scenarios = json.load(f)
            for i, scenario in enumerate(scenarios):
                if "id" not in scenario:
                    scenario["id"] = i + 1
            return scenarios
        except Exception as e:
            logger.error(f"Error loading scenarios: {e}")
            return []

    def find_similar_scenarios(
        self, query: str, limit: int = 3
    ) -> List[Tuple[str, str, float]]:
        """Ищет похожие сценарии по запросу"""
        if not query.strip():
            return []

        try:
            similar_scenarios = self.database.search_similar(query.strip(), limit)
            logger.info(
                f"Found {len(similar_scenarios)} similar scenarios for query: {query}"
            )
            return similar_scenarios
        except Exception as e:
            logger.error(f"Failed to search similar scenarios: {e}")
            return []

    def get_scenarios_count(self) -> int:
        """Возвращает количество сценариев в базе"""
        try:
            return self.database.get_scenarios_count()
        except Exception as e:
            logger.error(f"Failed to get scenarios count: {e}")
            return 0

    def format_response(self, scenarios: List[Tuple[str, str, float]]) -> str:
        """Форматирует ответ для пользователя"""
        if not scenarios:
            return "К сожалению, я не нашел подходящего ответа на ваш вопрос. Попробуйте переформулировать."

        response = "Найденные ответы:\n\n"
        for answer in scenarios:
            response += f"{answer[1]}\n\n"

        response += "Если ответ не подходит, переформулируйте вопрос."
        return response
