# Установка базового образа
FROM python:3.10-alpine

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование зависимостей в контейнер
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода бота в контейнер
COPY . .

# Команда, которая будет выполнена при запуске контейнера
CMD [ "python", "main.py" ]
