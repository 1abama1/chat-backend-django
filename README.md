
# Django Chat Backend

Backend для мессенджера на Django с поддержкой WebSocket, JWT-авторизации и real-time обмена сообщениями.  
Проект собран как production-ready пример архитектуры Django + Channels.

Подходит для pet-проекта, портфолио и демонстрации навыков backend-разработки.

---

## Стек

- Python 3.11
- Django 5.2
- Django REST Framework
- Django Channels (ASGI / WebSocket)
- PostgreSQL
- Redis
- JWT (SimpleJWT)
- Swagger / OpenAPI
- Docker, Docker Compose
- GitHub Actions (CI)

---

## Функциональность

- JWT авторизация (access / refresh)
- Private и group чаты
- Real-time сообщения через WebSocket
- Online / offline статус пользователей
- Typing indicator
- Read / delivered статусы сообщений
- Unread счётчики по чатам
- Пересылка сообщений
- Редактирование и удаление сообщений
- Закреплённые сообщения
- Поиск по сообщениям
- Swagger документация API

---

## Структура проекта

```

backend/
├── backend/
│   ├── settings.py
│   ├── asgi.py
│   ├── urls.py
│   ├── routing.py
│   ├── jwt_middleware.py
│   └── middleware.py
├── users/            # Пользователи и online/offline статус
├── chats/            # Чаты и состояния прочтения
├── chat_messages/    # Сообщения, статусы, pinned, forward
└── manage.py

````

---

## Запуск через Docker

### 1. Клонирование репозитория

```bash
git clone <repo-url>
cd DjangoProject
````

---

### 2. Переменные окружения

Создайте файл `.env` в корне проекта:

```env
DEBUG=1
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=*

DB_NAME=chat
DB_USER=chat
DB_PASSWORD=chat
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
```

---

### 3. Запуск

```bash
docker compose down -v
docker compose up --build
```

При запуске backend автоматически:

* ждёт готовности PostgreSQL
* ждёт готовности Redis
* применяет миграции
* запускает ASGI сервер (Daphne)

---

### 4. Создание суперпользователя

```bash
docker compose exec backend python manage.py createsuperuser
```

---

## Доступные сервисы

* Admin panel: [http://localhost:8000/admin/](http://localhost:8000/admin/)
* Swagger UI: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
* OpenAPI schema: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

---

## Authentication

### Login

POST /api/auth/login/

Request body:
```json
{
  "username": "string",
  "password": "string"
}
```

Response:

```json
{
  "access": "string",
  "refresh": "string"
}
```

---

### Refresh token

POST /api/auth/refresh/

Request body:

```json
{
  "refresh": "string"
}
```

Response:

```json
{
  "access": "string"
}
```

---

### Registration

POST /api/auth/register/

Request body:

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

Response:

```json
{
  "user": {
    "id": 1,
    "username": "string",
    "email": "string"
  },
  "access": "string",
  "refresh": "string"
}
```

После регистрации пользователь считается авторизованным — повторный login не требуется.

---

### Использование access-токена

```
Authorization: Bearer <access_token>
```

---

## WebSocket

### Подключение

```
ws://localhost:8000/ws/chat/{chat_id}/?token={JWT}
```

---

### События клиента

Отправка сообщения:

```json
{
  "type": "message",
  "text": "Hello"
}
```

Typing indicator:

```json
{
  "type": "typing",
  "is_typing": true
}
```

Read:

```json
{
  "type": "read",
  "last_read_message_id": 123
}
```

Forward:

```json
{
  "type": "forward",
  "message_id": 15,
  "target_chat_id": 3
}
```

Edit:

```json
{
  "type": "edit",
  "message_id": 42,
  "text": "Updated text"
}
```

Delete:

```json
{
  "type": "delete",
  "message_id": 42
}
```

---

### События сервера

Новое сообщение:

```json
{
  "type": "message",
  "message_id": 123,
  "text": "Hello",
  "sender": "username",
  "created_at": "2024-01-01T12:00:00Z"
}
```

Typing:

```json
{
  "type": "typing",
  "user_id": 2,
  "is_typing": true
}
```

Read:

```json
{
  "type": "read",
  "user_id": 2,
  "last_read_message_id": 123
}
```

Online / offline:

```json
{
  "type": "user_status",
  "user_id": 2,
  "is_online": true
}
```

---

## Тестирование

```bash
docker compose exec backend python manage.py test
```

---

## Миграции

```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

---

## Локальный запуск без Docker

```bash
pip install -r requirements.txt
python backend/manage.py migrate
python backend/manage.py runserver
```

Для WebSocket:

```bash
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```

---

## CI

В проекте настроен GitHub Actions CI:

* PostgreSQL и Redis через services
* применение миграций
* Django system check

---

## Production заметки

* DEBUG должен быть выключен
* SECRET_KEY хранить в переменных окружения
* ALLOWED_HOSTS настроить явно
* использовать Nginx как reverse proxy
* включить HTTPS
* разделить dev и prod конфигурации

---

## Архитектурные моменты

* ASGI + Channels
* JWT авторизация для WebSocket
* Явный `django.setup()` для Django 5.x
* Lazy imports в consumers
* Автоматический старт через entrypoint
* Custom User модель