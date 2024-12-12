# Використовуємо базовий образ Python
FROM python:3.9-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файл залежностей та встановлюємо їх
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код у контейнер
COPY . .

# Відкриваємо порт для Flask
EXPOSE 5000

# Вказуємо команду для запуску додатка
CMD ["python", "run.py"]

