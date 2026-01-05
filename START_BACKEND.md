# 🚀 Запуск Backend

## ✅ Исправление проблемы с порядком запуска

Проблема была в том, что Django пытался подключиться к PostgreSQL до того, как база данных была готова принимать соединения.

### Решение

Используется **production-ready подход**:

1. **Healthcheck для PostgreSQL** - Docker Compose ждет готовности БД
2. **wait-for-it.sh** - дополнительная проверка готовности сервисов
3. **entrypoint.sh** - автоматическое ожидание БД и выполнение миграций

## 🛠 Как запустить

### 1. Остановите старые контейнеры (если есть)

```powershell
docker compose down -v
```

### 2. Пересоберите и запустите

```powershell
docker compose up --build
```

### 3. Проверьте логи

Вы должны увидеть:

```
backend-1  | Waiting for PostgreSQL to be ready...
backend-1  | wait-for-it.sh: db:5432 is available after X seconds
backend-1  | Waiting for Redis to be ready...
backend-1  | wait-for-it.sh: redis:6379 is available after X seconds
backend-1  | Running migrations...
backend-1  | Starting server...
backend-1  | Starting server at tcp:port=8000:interface=0.0.0.0
```

### 4. Создайте суперпользователя (если нужно)

В новом терминале:

```powershell
docker compose exec backend python manage.py createsuperuser
```

## ✅ Проверка

1. **Админ панель**: http://localhost:8000/admin/
2. **Swagger UI**: http://localhost:8000/api/docs/
3. **API Schema**: http://localhost:8000/api/schema/

## 🔍 Что происходит под капотом

### Docker Compose

```yaml
depends_on:
  db:
    condition: service_healthy  # Ждет healthcheck
```

### Healthcheck PostgreSQL

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U chat -d chat"]
  interval: 5s
  timeout: 5s
  retries: 5
```

### Entrypoint Script

1. Ждет готовности PostgreSQL (до 30 секунд)
2. Ждет готовности Redis (до 10 секунд)
3. Выполняет миграции автоматически
4. Устанавливает `DJANGO_SETTINGS_MODULE=backend.settings`
5. Запускает Daphne сервер

**Важно:** `DJANGO_SETTINGS_MODULE` устанавливается явно, так как ASGI-сервер запускается вне `manage.py` и Django 5.x требует явного указания settings модуля.

## 🐛 Если что-то не работает

### Проверьте логи

```powershell
docker compose logs backend
docker compose logs db
```

### Проверьте статус контейнеров

```powershell
docker compose ps
```

Все сервисы должны быть в статусе `Up` и `healthy`.

### Пересоздайте контейнеры

```powershell
docker compose down -v
docker compose up --build
```

## 📝 Полезные команды

### Просмотр логов в реальном времени

```powershell
docker compose logs -f backend
```

### Выполнить команду Django

```powershell
docker compose exec backend python manage.py <command>
```

### Создать миграции

```powershell
docker compose exec backend python manage.py makemigrations
```

### Применить миграции вручную

```powershell
docker compose exec backend python manage.py migrate
```

### Открыть shell Django

```powershell
docker compose exec backend python manage.py shell
```

### Остановить все

```powershell
docker compose down
```

### Остановить и удалить volumes (БД)

```powershell
docker compose down -v
```

## 🎉 Готово!

Теперь backend должен запускаться автоматически и корректно ждать готовности всех зависимостей.
