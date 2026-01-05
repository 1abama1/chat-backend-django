# Django Chat Backend

Полноценный backend для мессенджера на Django с поддержкой WebSocket, JWT авторизации, real-time сообщений и всех необходимых функций.

## 🚀 Технологии

- **Django 5.2** - основной фреймворк
- **Django REST Framework** - REST API
- **Django Channels** - WebSocket поддержка
- **PostgreSQL** - база данных
- **Redis** - для Channels
- **JWT** - авторизация
- **Swagger** - документация API
- **Docker** - контейнеризация

## ✨ Функционал

- ✅ JWT авторизация (login/refresh)
- ✅ Private и Group чаты
- ✅ Real-time сообщения через WebSocket
- ✅ Статусы сообщений (delivered/read)
- ✅ Online/Offline статусы пользователей
- ✅ Typing indicator
- ✅ Forward messages
- ✅ Edit/Delete сообщений
- ✅ Pinned messages
- ✅ Поиск сообщений
- ✅ Unread counters
- ✅ Swagger документация

## 📁 Структура проекта

```
backend/
├── backend/          # Основные настройки Django
│   ├── settings.py   # Конфигурация
│   ├── asgi.py       # ASGI для WebSocket
│   ├── urls.py       # URL маршруты
│   ├── routing.py    # WebSocket маршруты
│   ├── middleware.py # JWT middleware для WS
│   └── jwt_middleware.py
├── users/            # Пользователи и статусы
├── chats/            # Чаты и read states
├── chat_messages/   # Сообщения, статусы, pinned
└── manage.py
```

## 🛠 Установка и запуск

### 1. Клонируйте репозиторий

```bash
git clone <your-repo>
cd DjangoProject
```

### 2. Создайте .env файл

```env
DEBUG=1
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=*

DB_NAME=chat
DB_USER=chat
DB_PASSWORD=chat
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
```

### 3. Запустите через Docker

```bash
docker compose down -v  # Очистить старые данные (опционально)
docker compose up --build
```

**Важно:** Backend автоматически:
- ✅ Ждет готовности PostgreSQL (healthcheck)
- ✅ Ждет готовности Redis
- ✅ Выполняет миграции автоматически
- ✅ Запускает сервер

### 4. Создайте суперпользователя

В новом терминале:

```bash
docker compose exec backend python manage.py createsuperuser
```

📖 **Подробнее:** См. [START_BACKEND.md](START_BACKEND.md) для детальных инструкций

## 📡 API Endpoints

### Авторизация

- `POST /api/auth/login/` - Получить JWT токен
- `POST /api/auth/refresh/` - Обновить токен

### Чаты

- `GET /api/chats/` - Список чатов пользователя
- `POST /api/chats/` - Создать чат
- `GET /api/chats/{id}/` - Детали чата
- `PUT /api/chats/{id}/` - Обновить чат
- `DELETE /api/chats/{id}/` - Удалить чат

### Сообщения

- `GET /api/messages/?chat={chat_id}` - Получить сообщения чата
- `POST /api/messages/` - Отправить сообщение
- `PUT /api/messages/{id}/` - Редактировать сообщение
- `DELETE /api/messages/{id}/` - Удалить сообщение
- `GET /api/messages/search/?q={query}` - Поиск сообщений

### Pinned Messages

- `GET /api/pinned/?chat={chat_id}` - Закрепленные сообщения
- `POST /api/pinned/` - Закрепить сообщение
- `DELETE /api/pinned/{id}/` - Открепить сообщение

### Пользователи

- `GET /api/users/` - Список пользователей
- `GET /api/users/me/` - Текущий пользователь

### Документация

- `GET /api/docs/` - Swagger UI
- `GET /api/schema/` - OpenAPI схема

## 🔌 WebSocket

### Подключение

```
ws://localhost:8000/ws/chat/{chat_id}/?token={jwt_token}
```

### Отправка сообщений

```json
{
  "type": "message",
  "text": "Привет!"
}
```

### Typing indicator

```json
{
  "type": "typing",
  "is_typing": true
}
```

### Отметить прочитанным

```json
{
  "type": "read",
  "last_read_message_id": 123
}
```

### Переслать сообщение

```json
{
  "type": "forward",
  "message_id": 15,
  "target_chat_id": 3
}
```

### Редактировать сообщение

```json
{
  "type": "edit",
  "message_id": 42,
  "text": "Новый текст"
}
```

### Удалить сообщение

```json
{
  "type": "delete",
  "message_id": 42
}
```

### Получение событий

```json
{
  "type": "message",
  "message_id": 123,
  "text": "Привет!",
  "sender": "username",
  "sender_id": 1,
  "created_at": "2024-01-01T12:00:00Z"
}
```

```json
{
  "type": "typing",
  "user_id": 2,
  "username": "user2",
  "is_typing": true
}
```

```json
{
  "type": "read",
  "user_id": 2,
  "last_read_message_id": 123
}
```

```json
{
  "type": "user_status",
  "user_id": 2,
  "is_online": true
}
```

## 🔐 JWT Авторизация

### Получение токена

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

Ответ:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Использование токена

```bash
curl -X GET http://localhost:8000/api/chats/ \
  -H "Authorization: Bearer {access_token}"
```

## 🧪 Тестирование

```bash
docker exec -it djangoproject-backend-1 python manage.py test
```

## 📝 Миграции

```bash
# Создать миграции
docker exec -it djangoproject-backend-1 python manage.py makemigrations

# Применить миграции
docker exec -it djangoproject-backend-1 python manage.py migrate
```

## 🏗 Разработка

### Локальная разработка без Docker

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте PostgreSQL и Redis локально

3. Запустите миграции:
```bash
python backend/manage.py migrate
```

4. Запустите сервер:
```bash
python backend/manage.py runserver
```

5. Запустите Daphne для WebSocket:
```bash
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```

## 📚 Модели данных

### User
- Стандартные поля Django User
- Связан с UserStatus

### UserStatus
- `is_online` - онлайн статус
- `last_seen` - последний раз онлайн

### Chat
- `type` - private/group
- `name` - название (опционально для private)
- `members` - участники (M2M)

### ChatReadState
- `chat` - чат
- `user` - пользователь
- `last_read_message_id` - последнее прочитанное сообщение

### Message
- `chat` - чат
- `sender` - отправитель
- `text` - текст
- `forwarded_from` - оригинальное сообщение (для пересылки)
- `is_edited` - редактировано
- `is_deleted` - удалено

### MessageStatus
- `message` - сообщение
- `user` - пользователь
- `delivered` - доставлено
- `read` - прочитано

### PinnedMessage
- `chat` - чат
- `message` - сообщение
- `pinned_by` - кто закрепил

## 🚀 Production

Для production:

1. Измените `DEBUG=0` в `.env`
2. Установите надежный `SECRET_KEY`
3. Настройте `ALLOWED_HOSTS`
4. Используйте Nginx как reverse proxy
5. Настройте SSL сертификаты
6. Используйте production-ready настройки PostgreSQL и Redis
