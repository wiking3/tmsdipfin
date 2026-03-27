FROM python:3.12-slim AS builder          #1й этап multi-stage качаем все необходимые библиотеки и компиляторы для python
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \           #Отключает создание .pyc файлов 
    PYTHONUNBUFFERED=1                    #Включает вывод stdout и stderr - если Python приложение упадет - то в лог докер-контенера выпадет error          


RUN apt-get update && apt-get install -y --no-install-recommends \          # качаем все необходимые библиотеки и компиляторы для python
    pkg-config \                                                            # помогает искать зависимости для python-приложения
    default-libmysqlclient-dev  \                                           # модуль для раработы с MySQL
    build-essential \                                                       # компиляторы и утилиты для компиляции
    && rm -rf /var/lib/apt/lists/*                                          # удаляет кэш пакетов

COPY requirements.txt .                                                    
# Копируем wheels для кэширования
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt         # собираем whl-файл для пакетов из requirements.txt в директорию /wheels  

# Финальный образ
FROM python:3.12-slim                     # 2й этап  multi-stage  
WORKDIR /app                              

# Только runtime зависимости MySQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev  \
    && rm -rf /var/lib/apt/lists/*

# Копируем wheels и устанавливаем
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY . .
RUN chmod +x flask-entrypoint.sh
EXPOSE 5000
CMD ["./flask-entrypoint.sh"]
