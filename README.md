# Проект Nice Answer

## Как запустить проект через Docker Compose (Настоятельно рекомендуется!)
Поскольку проект использует микросервисную архитектуру (PostgreSQL, Redis, Celery, Centrifugo, Maildev), самый быстрый и надежный способ запуска — через Docker.

1. Убедитесь, что у вас установлен Docker и Docker Desktop запущен.
2. Скопируйте файл `.env.example` и переименуйте его в `.env.docker`.
3. Скопируйте файл `centrifugo.example.json` и переименуйте его в `centrifugo.json`.
4. В терминале в корне проекта выполните команду для сборки и запуска контейнеров в фоновом режиме:
   `docker compose up --build -d`
5. Примените миграции внутри контейнера веб-сервера для создания структуры БД:
   `docker compose exec web python manage.py migrate`
6. Сгенерируйте тестовые данные (пользователей, теги, вопросы, ответы):
   `docker compose exec web python manage.py fill_db --ratio 10`
7. Создайте суперпользователя для доступа в панель управления:
   `docker compose exec web python manage.py createsuperuser`
8. Проект будет доступен по адресу: http://127.0.0.1:8000/
9. **Для просмотра тестовых email-уведомлений откройте интерфейс Maildev:** http://127.0.0.1:1080/

## Как запустить проект локально (Без Docker)
> Для полноценной работы всех функций (веб-сокеты, кэш, фоновые задачи, email) вам потребуется вручную установить и запустить PostgreSQL, Redis, Centrifugo и Maildev, а также открыть отдельные терминалы для запуска `celery worker` и `celery beat`.

1. Убедитесь, что у вас установлен Python версии 3.12 или выше.
2. Создайте виртуальное окружение:
   `python -m venv venv`
3. Активируйте виртуальное окружение:
   * Windows: `venv\Scripts\activate`
   * Mac/Linux: `source venv/bin/activate`
4. Установите зависимости:
   `pip install -r requirements.txt`
5. Настройте и запустите необходимые базы данных и сервисы (включая создание файла `centrifugo.json` из шаблона).
6. Скопируйте файл `.env.example` в `.env.local` и заполните его своими данными для локального подключения.
7. Примените миграции для создания таблиц в базе данных:
   `python manage.py migrate`
8. Заполните базу тестовыми данными:
   `python manage.py fill_db --ratio 10`
9. Запустите локальный сервер Django:
   `python manage.py runserver`
