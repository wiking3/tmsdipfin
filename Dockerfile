FROM python:3.12-slim AS builder           
WORKDIR /app
#python logs to stdout 
ENV PYTHONDONTWRITEBYTECODE=1 \           #Отключает создание .pyc файлов 
    PYTHONUNBUFFERED=1                    #Включает вывод stdout и stderr - если Python приложение упадет - то в лог докер-контенера выпадет error          

# install only compiliers for build 
RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    default-libmysqlclient-dev  \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Копируем wheels для кэширования
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Финальный образ
FROM python:3.12-slim
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
