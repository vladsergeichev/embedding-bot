# 🤖 Банковский Консультант - Telegram Bot с векторным поиском

Минимальный проект для изучения векторных баз данных на примере Telegram-бота для банковских консультаций.

## Стек
- **Python**: 3.12.10
- **Telegram Bot**: aiogram 3.7.0
- **Vector Database**: Qdrant
- **Embeddings**: sentence-transformers 2.5.1 (многоязычная модель)

## Запуск
### 1. Подготовка
1. Клонировать репозиторий:
```bash
git clone <repository-url>
cd embedding-bot
```

2. Создать файл `.env` токеном бота из [@BotFather](https://t.me/BotFather):
```bash
BOT_TOKEN=your_actual_bot_token_here
```

### 2. Запуск
```bash
docker-compose up --build
```

Бот автоматически:
- Запустит Qdrant
- Создаст коллекцию
- Загрузит сценарии в векторную БД
- Запустит Telegram бота

### 3. Тестирование
1. Открыть бота в Telegram
2. Отправить `/start`
3. Задать вопрос о банковских услугах, например:
   - "Как оформить кредит?"
   - "Какие документы нужны для карты?"
   - "Как пополнить карту?"
