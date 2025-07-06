# Банковский Консультант

Telegram-бота с векторным поиском

## Стек
- **Python**: 3.12.10
- **Telegram Bot**: aiogram 3.7.0
- **Vector Database**: Qdrant
- **Embeddings**: sentence-transformers

## Quick Start
### 1. Подготовка
1. Клонировать репозиторий:
```bash
git clone https://github.com/vladsergeichev/embedding-bot.git
cd embedding-bot
```

2. Создать файл `.env` токеном бота из [@BotFather](https://t.me/BotFather):
```bash
BOT_TOKEN=telegram_bot_token
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
Время запуска ~5-7 минут.

### 3. Тестирование
1. Открыть бота в Telegram
2. Отправить `/start`
3. Задать вопрос о банковских услугах, например:
   - "Как оформить кредит?"
   - "Какие документы нужны для карты?"
   - "Как пополнить карту?"
