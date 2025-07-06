FROM python:3.12.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data ./data

CMD ["python", "-m", "src.bot.main"] 