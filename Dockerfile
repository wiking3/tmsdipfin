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
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt         # собираем whl-файл для пакетов из requirements.txt в директорию /wheels  


FROM python:3.12-slim                     # 2й этап  multi-stage - runtime 
WORKDIR /app                              


RUN apt-get update && apt-get install -y --no-install-recommends \       # Только runtime зависимости MySQL
    default-libmysqlclient-dev  \
    && rm -rf /var/lib/apt/lists/*


COPY --from=builder /wheels /wheels                                     # Из 1ого этапа копируем  whl-файлы без зафисимостей и мусора
RUN pip install --no-cache-dir /wheels/*                                # устанавливаем whl-архивы в папку /wheels/

COPY . .                                                                
RUN chmod +x flask-entrypoint.sh                                        
EXPOSE 5000
CMD ["./flask-entrypoint.sh"]                                           # определяем что докер-контейнер при запуске выполняет bash-скрипт (так как нам нужно выполнить команды flask db init, flask db migrate -m 'create initial tables',
                                                                          flask db upgrade + подождать пока подымется контенер с MySQL и создать пользователей через  flask create-user  user pass и в конце запустить Flask-приложение : exec  flask run --host 0.0.0.0 --port 5000 )
