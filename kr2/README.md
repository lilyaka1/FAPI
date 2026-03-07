# Контрольная работа №2 - Advanced FastAPI

Расширенная работа с FastAPI: валидация данных, работа с продуктами, аутентификация с cookies и работа с HTTP-заголовками.

## Содержание папки

```
kr2/
├── app.py                # Основное приложение (задания 3.1, 3.2, 5.1, 5.4, 5.5)
├── auth_advanced.py      # Приложение с продвинутой аутентификацией (задания 5.2, 5.3)
├── models.py             # Pydantic модели для валидации данных
└── README.md             # Этот файл
```

## Задания

### Задание 3.1 - Create User
**Endpoint:** `POST /create_user`

Создание пользователя с валидацией данных через Pydantic модель `UserCreate`.

**Параметры:**
- `name` (str, обязательно): имя пользователя
- `email` (str, обязательно): валидный email адрес (используется EmailStr)
- `age` (int, опционально): положительное целое число
- `is_subscribed` (bool, опционально): статус подписки (по умолчанию `false`)

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/create_user" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "email": "alice@example.com",
    "age": 30,
    "is_subscribed": true
  }'
```

**Пример ответа:**
```json
{
  "name": "Alice",
  "email": "alice@example.com",
  "age": 30,
  "is_subscribed": true
}
```

### Задание 3.2 - Products API
**Endpoints:**
- `GET /product/{product_id}` - получить товар по ID
- `GET /products/search` - поиск товаров

**Важно:** Маршрут `/products/search` должен быть объявлен ПЕРЕД `/product/{product_id}`, иначе FastAPI будет пытаться преобразовать "search" в целое число.

**Параметры GET /product/{product_id}:**
- `product_id` (int, обязательно): ID товара

**Параметры GET /products/search:**
- `keyword` (str, обязательно): ключевое слово для поиска
- `category` (str, опционально): фильтр по категории
- `limit` (int, опционально): максимальное количество результатов (по умолчанию 10)

**Примеры запросов:**
```bash
# Получить товар по ID
curl "http://localhost:8000/product/123"

# Поиск товаров
curl "http://localhost:8000/products/search?keyword=phone&category=Electronics&limit=5"
```

### Задание 5.1 - Cookie Authentication
**Endpoints:**
- `POST /login` - вход в систему
- `GET /user` - получить профиль пользователя

Аутентификация через безопасные HTTP-only cookies с уникальным session_token (UUID).

**Учетные данные для тестирования:**
- username: `user123`, password: `password123`
- username: `admin`, password: `admin123`

**Пример запроса логина:**
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user123", "password": "password123"}' \
  -c cookies.txt
```

**Пример запроса профиля:**
```bash
curl "http://localhost:8000/user" -b cookies.txt
```

### Задание 5.2 - Signed Cookies (auth_advanced.py)
**Endpoints:**
- `POST /login` - вход с подписанным cookie
- `GET /profile` - получить профиль

Использует библиотеку `itsdangerous` для создания криптографически подписанных cookies.

**Формат session_token:** `<user_id>.<signature>`

**Запуск:**
```bash
uvicorn auth_advanced:app --reload --port 8001
```

### Задание 5.3 - Advanced Sessions (auth_advanced.py)
**Endpoints:**
- `POST /login_advanced` - вход с управлением сессией
- `GET /profile_advanced` - получить профиль с автопродлением

Логика управления сессией (время жизни 5 минут):
- **< 3 минут с последней активности:** кука НЕ обновляется
- **>= 3 и <= 5 минут:** кука обновляется с новым временем
- **> 5 минут:** сессия истекла (401 ошибка)

**Формат session_token:** `<user_id>.<timestamp>.<signature>`

### Задание 5.4 - Extract Headers
**Endpoint:** `GET /headers`

Извлечение заголовков из HTTP запроса.

**Обязательные заголовки:**
- `User-Agent`
- `Accept-Language`

**Пример запроса:**
```bash
curl -H "User-Agent: Mozilla/5.0" \
     -H "Accept-Language: en-US,en;q=0.9" \
     "http://localhost:8000/headers"
```

**Пример ответа:**
```json
{
  "User-Agent": "Mozilla/5.0",
  "Accept-Language": "en-US,en;q=0.9"
}
```

### Задание 5.5 - Headers Model
**Endpoints:**
- `GET /headers_model` - получить заголовки
- `GET /info` - получить информацию с заголовками и X-Server-Time

Использует Pydantic параметры Header для валидации и переиспользования кода.

**Пример запроса:**
```bash
curl -H "User-Agent: Mozilla/5.0" \
     -H "Accept-Language: en-US,en;q=0.9" \
     "http://localhost:8000/info"
```

**Пример ответа:**
```json
{
  "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
  "headers": {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
  }
}
```

**Ответные заголовки включают:**
- `X-Server-Time: 2025-04-16T12:34:56` (текущее серверное время)

## Быстрый старт

### Установка зависимостей
```bash
pip install fastapi uvicorn pydantic email-validator itsdangerous
```

### Запуск основного приложения (задания 3.1-3.2, 5.1, 5.4-5.5)
```bash
cd kr2
uvicorn app:app --reload
```

Приложение доступно по адресу: `http://localhost:8000`

### Запуск приложения с продвинутой аутентификацией (задания 5.2-5.3)
```bash
cd kr2
uvicorn auth_advanced:app --reload --port 8001
```

Приложение доступно по адресу: `http://localhost:8001`

## Тестирование

### Использование curl
```bash
# Задание 3.1
curl -X POST "http://localhost:8000/create_user" \
  -H "Content-Type: application/json" \
  -d '{"name":"Bob","email":"bob@example.com","age":25,"is_subscribed":true}'

# Задание 3.2
curl "http://localhost:8000/products/search?keyword=phone"
curl "http://localhost:8000/product/123"

# Задание 5.1
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user123","password":"password123"}' \
  -c cookies.txt
curl "http://localhost:8000/user" -b cookies.txt

# Задание 5.4
curl "http://localhost:8000/headers" \
  -H "User-Agent: TestAgent" \
  -H "Accept-Language: en-US"
```

### Использование Postman
1. Создайте collection
2. Добавьте запросы для каждого endpoint'а
3. Для cookie-based endpoints: в настройках вкладки "Cookies" добавьте необходимые значения

## Интерактивная документация

### FastAPI Swagger UI
- app.py: `http://localhost:8000/docs`
- auth_advanced.py: `http://localhost:8001/docs`

### FastAPI ReDoc
- app.py: `http://localhost:8000/redoc`
- auth_advanced.py: `http://localhost:8001/redoc`

## Требования

- Python 3.7+
- FastAPI 0.68+
- Uvicorn
- Pydantic 2.0+
- email-validator (для EmailStr)
- itsdangerous (для подписанных cookies)

## Примечания

- Все данные хранятся в памяти приложения и теряются при перезагрузке
- Для production среды необходимо: использовать `secure=True` для cookies, изменить SECRET_KEY, добавить HTTPS
- Валидация Accept-Language содержит простой regex-паттерн и может требовать доработки в production
- Sessions в задании 5.3 хранятся в памяти; для production используйте Redis или БД
