from fastapi import FastAPI, HTTPException, Response, Cookie
import uuid
import time
from typing import Optional
from datetime import datetime
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired
from models import LoginRequest

app = FastAPI(title="KR2 Auth Advanced", version="1.0.0")

# Секретный ключ для подписи
SECRET_KEY = "your-secret-key-change-in-production"
signer = TimestampSigner(SECRET_KEY)

# Хранилище пользователей
users = {
    "user123": "password123",
    "admin": "admin123"
}

# Хранилище активных сессий (для 5.3)
active_sessions = {}  # format: {user_id: {created_at, last_activity}}


# ==================== ЗАДАНИЕ 5.2 - Signed Cookies ====================
@app.post("/login")
def login_signed(credentials: LoginRequest, response: Response):
    """
    Вход в систему с подписанным cookie.
    
    Формат session_token: <user_id>.<signature>
    """
    # Проверка учетных данных
    if credentials.username not in users or users[credentials.username] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Создание уникального user_id (UUID)
    user_id = str(uuid.uuid4())
    
    # Создание подписанного значения
    session_value = signer.sign(user_id).decode('utf-8')
    
    # Установка cookie
    response.set_cookie(
        key="session_token",
        value=session_value,
        httponly=True,
        secure=False,  # False для локального тестирования
        max_age=300,   # 5 минут
        samesite="lax"
    )
    
    return {
        "message": "Successfully logged in",
        "user_id": user_id
    }


@app.get("/profile")
def get_profile_signed(session_token: Optional[str] = Cookie(None)):
    """
    Получить профиль пользователя с проверкой подписи cookie.
    """
    if not session_token:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})
    
    try:
        # Проверка и извлечение user_id из подписанного значения
        user_id = signer.unsign(session_token).decode('utf-8')
        
        return {
            "username": "user123",
            "email": "user123@example.com",
            "user_id": user_id
        }
    except BadSignature:
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})
    except Exception as e:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})


# ==================== ЗАДАНИЕ 5.3 - Session with Auto-Renewal ====================
@app.post("/login_advanced")
def login_advanced(credentials: LoginRequest, response: Response):
    """
    Вход с расширенной управлением сессией.
    
    Формат session_token: <user_id>.<timestamp>.<signature>
    
    Сессия автоматически продлевается, если:
    - Прошло >= 3 и <= 5 минут с последней активности
    - Если прошло > 5 минут - сессия истекла
    - Если прошло < 3 минут - кука не обновляется
    """
    # Проверка учетных данных
    if credentials.username not in users or users[credentials.username] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Создание уникального user_id (UUID)
    user_id = str(uuid.uuid4())
    
    # Текущее время (UNIX timestamp)
    current_timestamp = int(time.time())
    
    # Создание строки для подписи: user_id.timestamp
    session_data = f"{user_id}.{current_timestamp}"
    session_signature = signer.sign(session_data).decode('utf-8')
    
    # Сохранение информации о сессии
    active_sessions[user_id] = {
        "created_at": current_timestamp,
        "last_activity": current_timestamp,
        "username": credentials.username
    }
    
    # Установка cookie с полными данными
    response.set_cookie(
        key="session_token",
        value=session_signature,
        httponly=True,
        secure=False,
        max_age=300,  # 5 минут
        samesite="lax"
    )
    
    return {"message": "Successfully logged in"}


@app.get("/profile_advanced")
def get_profile_advanced(session_token: Optional[str] = Cookie(None), response: Response = Response()):
    """
    Получить профиль с проверкой времени жизни сессии.
    
    Логика:
    - Если >= 5 минут с последней активности: 401 Session expired
    - Если < 3 минут: возвращаем данные, кука НЕ обновляется
    - Если >= 3 и < 5 минут: возвращаем данные и обновляем куку
    """
    if not session_token:
        response.status_code = 401
        return {"message": "Session expired"}
    
    try:
        # Извлечение данных из подписи
        unsigned_data = signer.unsign(session_token).decode('utf-8')
        parts = unsigned_data.split('.')
        
        if len(parts) != 2:
            response.status_code = 401
            return {"message": "Invalid session"}
        
        user_id, timestamp_str = parts
        
        try:
            activity_timestamp = int(timestamp_str)
        except ValueError:
            response.status_code = 401
            return {"message": "Invalid session"}
        
        # Проверка существования сессии
        if user_id not in active_sessions:
            response.status_code = 401
            return {"message": "Session expired"}
        
        session_info = active_sessions[user_id]
        current_time = int(time.time())
        time_since_activity = current_time - activity_timestamp
        
        # Проверка: если прошло > 5 минут (300 секунд)
        if time_since_activity > 300:
            response.status_code = 401
            return {"message": "Session expired"}
        
        # Обновление сессии если прошло >= 3 и <= 5 минут
        if 180 <= time_since_activity <= 300:
            new_timestamp = int(time.time())
            session_data = f"{user_id}.{new_timestamp}"
            new_signature = signer.sign(session_data).decode('utf-8')
            
            # Установка обновленной куки
            response.set_cookie(
                key="session_token",
                value=new_signature,
                httponly=True,
                secure=False,
                max_age=300,
                samesite="lax"
            )
            
            session_info["last_activity"] = new_timestamp
        
        return {
            "username": session_info["username"],
            "email": f"{session_info['username']}@example.com",
            "user_id": user_id,
            "session_renewed": 180 <= time_since_activity <= 300
        }
    
    except BadSignature:
        response.status_code = 401
        return {"message": "Invalid session"}
    except Exception as e:
        response.status_code = 401
        return {"message": "Invalid session"}


# ==================== Health Check ====================
@app.get("/")
def read_root():
    """Проверка работоспособности приложения."""
    return {
        "message": "Welcome to KR2 Auth Advanced API",
        "endpoints": {
            "5.2": ["POST /login", "GET /profile"],
            "5.3": ["POST /login_advanced", "GET /profile_advanced"]
        }
    }
