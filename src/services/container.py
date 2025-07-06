import logging
from typing import Optional

from src.config import AppConfig
from src.database.qdrant import QdrantDB
from src.services.consultation_service import ConsultationService

logger = logging.getLogger(__name__)


class ServiceContainer:
    """Контейнер для управления зависимостями"""

    def __init__(self, config: AppConfig):
        self.config = config
        self._database: Optional[QdrantDB] = None
        self._consultation_service: Optional[ConsultationService] = None

    def get_database(self) -> QdrantDB:
        """Возвращает экземпляр базы данных (Singleton)"""
        if self._database is None:
            logger.info(f"Creating QdrantDB with config: {self.config.database}")
            self._database = QdrantDB(self.config.database)
        return self._database

    def get_consultation_service(self) -> ConsultationService:
        """Возвращает сервис консультаций (Singleton)"""
        if self._consultation_service is None:
            database = self.get_database()
            self._consultation_service = ConsultationService(
                database, data_file=self.config.data_file
            )
        return self._consultation_service
