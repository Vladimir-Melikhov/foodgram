Вот полный и готовый файл `README.md` со всеми исправлениями (правильный бейдж, ссылки на проект/документацию, IP-адрес сервера).

Скопируйте этот код целиком и вставьте в файл `README.md` в корне вашего репозитория.

```markdown
# Foodgram - Продуктовый помощник

[![Foodgram Workflow](https://github.com/Vladimir-Melikhov/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/Vladimir-Melikhov/foodgram/actions/workflows/main.yml)

## Ссылки на проект

- [Проект Foodgram (доступен по адресу)](http://104.128.132.167/)
- [Документация к API (Redoc)](http://104.128.132.167/api/docs/)

## Описание проекта

**Foodgram** — это веб-приложение для публикации и обмена рецептами. Пользователи могут:

- Публиковать свои рецепты с фотографиями
- Добавлять рецепты в избранное
- Подписываться на других авторов
- Формировать список покупок на основе выбранных рецептов
- Скачивать список покупок в формате PDF

## Технологический стек

**Backend:**
- Python 3.11
- Django 4.2.16
- Django REST Framework 3.15.2
- PostgreSQL 13.10
- Gunicorn
- Djoser (аутентификация)

**Frontend:**
- React (готовый образ)

**Инфраструктура:**
- Docker & Docker Compose
- Nginx
- GitHub Actions (CI/CD)

## Установка и запуск проекта

### Локальный запуск

1. **Клонировать репозиторий:**

```bash
git clone [https://github.com/Vladimir-Melikhov/foodgram.git](https://github.com/Vladimir-Melikhov/foodgram.git)
cd foodgram

```

2. **Создать файл `.env` в папке `infra/`:**

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432

# Docker
DOCKER_USERNAME=your-dockerhub-username

```

3. **Запустить проект:**

```bash
cd infra
docker-compose up -d

```

4. **Выполнить миграции и собрать статику:**

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input

```

5. **Создать суперпользователя:**

```bash
docker-compose exec backend python manage.py createsuperuser

```

6. **Загрузить ингредиенты (опционально):**

```bash
docker-compose exec backend python manage.py load_ingredients data/ingredients.json

```

Проект будет доступен по адресу: [http://localhost/](https://www.google.com/search?q=http://localhost/)

### Деплой на сервер

Проект настроен на автоматический деплой через GitHub Actions при пуше в ветки `main` или `master`.

**Необходимые секреты в GitHub:**

* `DOCKER_USERNAME` — логин DockerHub
* `DOCKER_PASSWORD` — пароль DockerHub
* `HOST` — IP-адрес сервера
* `USER` — имя пользователя на сервере
* `SSH_KEY` — приватный SSH-ключ (содержимое файла id_rsa)
* `SSH_PASSPHRASE` — пароль от SSH-ключа (если есть)
* `TELEGRAM_TO` — ID Telegram-чата для уведомлений
* `TELEGRAM_TOKEN` — токен Telegram-бота

**На сервере должны быть установлены:**

* Docker
* Docker Compose
* Nginx (опционально, для SSL)

## API Документация

После запуска проекта документация доступна по адресу:

* [http://localhost/api/docs/](https://www.google.com/search?q=http://localhost/api/docs/) (локально)
* [http://104.128.132.167/api/docs/](https://www.google.com/url?sa=E&source=gmail&q=http://104.128.132.167/api/docs/) (на сервере)

### Основные эндпоинты:

**Пользователи:**

* `POST /api/users/` — регистрация
* `POST /api/auth/token/login/` — получение токена
* `GET /api/users/me/` — профиль текущего пользователя
* `PUT /api/users/me/avatar/` — загрузка аватара

**Рецепты:**

* `GET /api/recipes/` — список рецептов
* `POST /api/recipes/` — создание рецепта
* `GET /api/recipes/{id}/` — получение рецепта
* `PATCH /api/recipes/{id}/` — редактирование рецепта
* `DELETE /api/recipes/{id}/` — удаление рецепта

**Избранное и корзина:**

* `POST /api/recipes/{id}/favorite/` — добавить в избранное
* `DELETE /api/recipes/{id}/favorite/` — удалить из избранного
* `POST /api/recipes/{id}/shopping_cart/` — добавить в корзину
* `GET /api/recipes/download_shopping_cart/` — скачать список покупок

**Теги и ингредиенты:**

* `GET /api/tags/` — список тегов
* `GET /api/ingredients/` — список ингредиентов (с фильтрацией)

## Тестирование через Postman

1. Импортируйте коллекцию из файла `docs/openapi-schema.yml`
2. Или используйте готовые примеры запросов:

**Регистрация:**

```http
POST /api/users/
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "testuser",
  "first_name": "Test",
  "last_name": "User",
  "password": "TestPass123"
}

```

**Получение токена:**

```http
POST /api/auth/token/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "TestPass123"
}

```

**Авторизованные запросы:**

```http
Authorization: Token <your-token-here>

```

## Структура проекта

```
foodgram/
├── backend/              # Django backend
│   ├── api/             # API приложение
│   ├── recipes/         # Модели рецептов
│   ├── users/           # Модели пользователей
│   ├── foodgram/        # Настройки проекта
│   └── Dockerfile       # Docker-образ backend
├── frontend/            # React frontend (готовый образ)
├── infra/               # Инфраструктура
│   ├── docker-compose.yml           # Локальный запуск
│   ├── docker-compose.production.yml # Продакшн
│   └── nginx.conf       # Конфигурация Nginx
├── docs/                # API документация
└── .github/workflows/   # CI/CD pipeline

```

## Константы проекта

Все константы вынесены в файл `backend/foodgram/constants.py`:

* Максимальные длины полей
* Минимальные значения для валидации
* Другие настройки

## Управление проектом

**Остановить контейнеры:**

```bash
docker-compose down

```

**Посмотреть логи:**

```bash
docker-compose logs backend

```

**Зайти в контейнер:**

```bash
docker-compose exec backend bash

```

**Создать миграции:**

```bash
docker-compose exec backend python manage.py makemigrations

```

## Автор

Мелихов Владимир
[https://github.com/Vladimir-Melikhov/foodgram](https://github.com/Vladimir-Melikhov/foodgram)
