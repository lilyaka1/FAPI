from fastapi import FastAPI, HTTPException, Request, Header, Response, Cookie
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime, timedelta
import time
from typing import Optional, List
from models import UserCreate, Product, CommonHeaders, LoginRequest, UserProfile

app = FastAPI(title="KR2 API", version="1.0.0")

# ==================== Задание 3.2 - Sample Products ====================
sample_products = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99},
]

# ==================== Задание 5.1 и 5.2 - Session Storage ====================
sessions = {}  # format: {session_token: {user_id, username, password_hash, created_at}}
users = {
    "user123": "password123",
    "admin": "admin123"
}


# ==================== ЗАДАНИЕ 3.1 ====================
@app.post("/create_user")
def create_user(user: UserCreate):
    """
    Создать нового пользователя.
    
    Требования:
    - name: обязательное поле
    - email: обязательное, валидный email
    - age: опционально, положительное целое число
    - is_subscribed: опционально, по умолчанию False
    """
    return {
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "is_subscribed": user.is_subscribed
    }


# ==================== ЗАДАНИЕ 3.2 - ВАЖНО: /products/search ПЕРЕД /product/{product_id} ====================
@app.get("/products/search")
def search_products(
    keyword: str,
    category: Optional[str] = None,
    limit: Optional[int] = 10
):
    """
    Поиск товаров по ключевому слову и категории.
    
    Параметры:
    - keyword (обязательно): ключевое слово для поиска
    - category (опционально): фильтр по категории
    - limit (опционально): максимальное количество результатов (по умолчанию 10)
    """
    results = []
    
    for product in sample_products:
        # Проверка по ключевому слову
        if keyword.lower() in product["name"].lower() or keyword.lower() in product["category"].lower():
            # Проверка по категории (если указана)
            if category is None or product["category"].lower() == category.lower():
                results.append(product)
                if len(results) >= limit:
                    break
    
    return results


@app.get("/product/{product_id}")
def get_product(product_id: int):
    """
    Получить информацию о товаре по ID.
    
    Параметры:
    - product_id: идентификатор товара
    """
    for product in sample_products:
        if product["product_id"] == product_id:
            return product
    
    raise HTTPException(status_code=404, detail="Product not found")


# ==================== ЗАДАНИЕ 5.1 - Authentication with Cookies ====================
@app.post("/login")
def login(credentials: LoginRequest, response: Response):
    """
    Вход в систему.
    
    Устанавливает безопасный cookie session_token.
    """
    # Проверка учетных данных
    if credentials.username not in users or users[credentials.username] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Создание уникального session_token
    session_token = str(uuid.uuid4())
    
    # Сохранение сессии
    sessions[session_token] = {
        "username": credentials.username,
        "created_at": time.time()
    }
    
    # Установка cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,  # False для локального тестирования
        max_age=300,   # 5 минут
        samesite="lax"
    )
    
    return {"message": "Successfully logged in"}


@app.get("/user")
def get_user(session_token: Optional[str] = Cookie(None)):
    """
    Получить информацию о профиле пользователя.
    
    Требуется валидный session_token в cookies.
    """
    if not session_token or session_token not in sessions:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})
    
    session = sessions[session_token]
    return {
        "username": session["username"],
        "email": f"{session['username']}@example.com"
    }


# ==================== ЗАДАНИЕ 5.4 - HTTP Headers ====================
@app.get("/headers")
def get_headers(
    user_agent: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None)
):
    """
    Получить значения заголовков User-Agent и Accept-Language.
    
    Возвращает ошибку 400 если необходимые заголовки отсутствуют.
    """
    if not user_agent or not accept_language:
        raise HTTPException(status_code=400, detail="Required headers missing")
    
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }


# ==================== ЗАДАНИЕ 5.5 - Headers with Pydantic Model ====================
@app.get("/headers_model")
def get_headers_model(
    user_agent: str = Header(..., alias="User-Agent"),
    accept_language: str = Header(..., alias="Accept-Language")
):
    """
    Получить заголовки используя параметры Header.
    
    Эквивалент Pydantic модели для заголовков.
    """
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }


@app.get("/info")
def get_info(
    user_agent: str = Header(..., alias="User-Agent"),
    accept_language: str = Header(..., alias="Accept-Language"),
    response: Response = Response()
):
    """
    Получить информацию о заголовках с дополнительной ответной информацией.
    
    Устанавливает заголовок X-Server-Time в ответе.
    """
    # Устанавливаем заголовок X-Server-Time
    response.headers["X-Server-Time"] = datetime.now().isoformat()
    
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": user_agent,
            "Accept-Language": accept_language
        }
    }


# ==================== Health Check ====================
@app.get("/")
def read_root():
    """Проверка работоспособности приложения."""
    return {
        "message": "Welcome to KR2 API",
        "tasks": [
            "3.1 - Create User",
            "3.2 - Products Search and Get",
            "5.1 - Cookie Authentication",
            "5.4 - Extract Headers",
            "5.5 - Headers Model"
        ]
    }
