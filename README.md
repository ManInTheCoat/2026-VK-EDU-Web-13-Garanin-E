# Проект Nice Answer

## Как запустить проект локально (Без Docker)
1. Убедитесь, что у вас установлен Python версии 3.12 или выше.
2. Создайте виртуальное окружение:
    `python -m venv venv`
3. Активируйте виртуальное окружение:
   * Windows: `venv\Scripts\activate`
   * Mac/Linux: `source venv/bin/activate`
4. Установите зависимости:
    `pip install -r requirements.txt`
5. Убедитесь, что у вас установлен и запущен PostgreSQL локально.
6. Скопируйте файл `.env.example` в `.env.local` и заполните его своими данными (или оставьте базовые для локальной разработки).
7. Примените миграции для создания таблиц в базе данных:
   `python manage.py migrate`
8. Заполните базу тестовыми данными:
   `python manage.py fill_db --ratio 10`
9. Запустите локальный сервер:
   `python manage.py runserver`

## Как запустить проект через Docker Compose (Рекомендуется)
1. Убедитесь, что у вас установлен Docker и Docker Desktop запущен.
2. Скопируйте файл `.env.example` и переименуйте его в `.env.docker`.
3. В терминале в корне проекта выполните команду для сборки и запуска контейнеров в фоновом режиме:
   `docker compose up --build -d`
4. Примените миграции внутри контейнера веб-сервера для создания структуры БД:
   `docker compose exec web python manage.py migrate`
5. Сгенерируйте тестовые данные (пользователей, теги, вопросы, ответы):
   `docker compose exec web python manage.py fill_db --ratio 10`
6. Создайте суперпользователя для доступа в панель управления:
   `docker compose exec web python manage.py createsuperuser`
7. Проект будет доступен по адресу: http://127.0.0.1:8000/
