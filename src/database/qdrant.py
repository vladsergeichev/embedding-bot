import logging
import time
from typing import List, Tuple

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from src.config import DatabaseConfig
from src.database.base import VectorDatabase

logger = logging.getLogger(__name__)


class QdrantDB(VectorDatabase):
    def __init__(
        self, config: DatabaseConfig, max_retries: int = 30, retry_delay: float = 2.0
    ):
        logger.info("Starting QdrantDB initialization...")
        self.config = config
        self.collection_name = config.collection_name

        # Загружаем модель эмбеддингов
        logger.info(f"Loading embedding model: {config.model_name}")
        start_time = time.time()
        self.embedding_model = SentenceTransformer(config.model_name)
        load_time = time.time() - start_time
        logger.info(f"Embedding model loaded in {load_time:.2f} seconds")

        self.vector_size = config.vector_size

        # Подключаемся к Qdrant
        logger.info("Connecting to Qdrant...")
        self.client = self._connect_with_retry(
            config.host, config.port, max_retries, retry_delay
        )

        # Создаем коллекцию если не существует
        self._ensure_collection_exists()
        logger.info("QdrantDB initialization completed")

    def _connect_with_retry(
        self, host: str, port: int, max_retries: int, retry_delay: float
    ) -> QdrantClient:
        """Подключается к Qdrant с повторными попытками"""
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Connecting to Qdrant {host}:{port} (attempt {attempt + 1})"
                )
                client = QdrantClient(host, port=port)
                client.get_collections()  # Проверка подключения
                logger.info("Qdrant connected successfully")
                return client
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Qdrant connection failed, retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"Failed to connect to Qdrant: {e}")
        raise Exception("Failed to connect to Qdrant after all attempts")

    def _ensure_collection_exists(self):
        """Создает коллекцию если она не существует"""
        try:
            self.client.get_collection(self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
        except Exception:
            logger.info(f"Creating new collection: {self.collection_name}")
            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size, distance=Distance.COSINE
                    ),
                )
                logger.info(f"Created new collection: {self.collection_name}")
            except Exception as create_error:
                # Если коллекция уже существует, это нормально
                if "already exists" in str(create_error):
                    logger.info(
                        f"Collection {self.collection_name} already exists, using it"
                    )
                else:
                    raise create_error

    def add_scenarios(self, scenarios: List[dict]):
        """Добавляет сценарии в базу данных"""
        if not scenarios:
            return

        logger.info(f"Starting to add {len(scenarios)} scenarios to Qdrant...")
        start_time = time.time()

        # Подготавливаем данные
        points = []
        for i, scenario in enumerate(scenarios):
            if i % 5 == 0:  # Логируем каждые 5 сценариев
                logger.info(f"Processing scenario {i+1}/{len(scenarios)}")

            # Создаем эмбеддинг для вопроса
            embedding = self.embedding_model.encode(scenario["question"]).tolist()  # type: ignore

            point = PointStruct(
                id=scenario["id"],
                vector=embedding,
                payload={
                    "question": scenario["question"],
                    "answer": scenario["answer"],
                },
            )
            points.append(point)

        # Добавляем точки в коллекцию
        logger.info("Uploading scenarios to Qdrant...")
        self.client.upsert(collection_name=self.collection_name, points=points)

        total_time = time.time() - start_time
        logger.info(
            f"Added {len(scenarios)} scenarios to Qdrant in {total_time:.2f} seconds"
        )

    def search_similar(
        self, query: str, limit: int = 3
    ) -> List[Tuple[str, str, float]]:
        """Ищет похожие сценарии по запросу"""
        # Создаем эмбеддинг для запроса
        query_embedding = self.embedding_model.encode([query]).tolist()[0]  # type: ignore

        # Ищем похожие векторы
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        # Формируем результат
        similar_scenarios = []
        for result in search_result:
            if result.payload:
                question = result.payload.get("question", "")
                answer = result.payload.get("answer", "")
                score = result.score
                similar_scenarios.append(
                    (question, answer, 1 - score)
                )  # Инвертируем score в distance

        return similar_scenarios

    def clear_scenarios(self):
        """Очищает коллекцию"""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size, distance=Distance.COSINE
            ),
        )
        logger.info("Cleared scenarios collection")

    def get_scenarios_count(self) -> int:
        """Возвращает количество сценариев в коллекции"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count or 0
        except Exception:
            return 0
