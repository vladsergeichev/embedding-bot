from abc import ABC, abstractmethod
from typing import List, Tuple


class VectorDatabase(ABC):
    """Базовый интерфейс для векторной базы данных"""

    @abstractmethod
    def add_scenarios(self, scenarios: List[dict]) -> None:
        """Добавляет сценарии в базу данных"""
        pass

    @abstractmethod
    def search_similar(
        self, query: str, limit: int = 3
    ) -> List[Tuple[str, str, float]]:
        """Ищет похожие сценарии по запросу"""
        pass

    @abstractmethod
    def clear_scenarios(self) -> None:
        """Очищает коллекцию сценариев"""
        pass

    @abstractmethod
    def get_scenarios_count(self) -> int:
        """Возвращает количество сценариев в базе"""
        pass
