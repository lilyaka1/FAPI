from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


# Задание 3.1
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the user")
    email: EmailStr = Field(..., description="Email of the user")
    age: Optional[int] = Field(None, ge=0, description="Age of the user (positive integer)")
    is_subscribed: Optional[bool] = Field(False, description="Newsletter subscription status")


# Задание 3.2 - Product model
class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float


# Задание 5.4 и 5.5
class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="User-Agent", description="User-Agent header")
    accept_language: str = Field(..., alias="Accept-Language", description="Accept-Language header")
    
    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, v):
        # Простая валидация формата Accept-Language
        # Примерный формат: en-US,en;q=0.9,es;q=0.8
        pattern = r'^[a-zA-Z]{2}(-[a-zA-Z]{2})?(\s*,\s*[a-zA-Z]{2}(-[a-zA-Z]{2})?(\s*;\s*q\s*=\s*0(\.\d{1,3})?)?)*$'
        if not re.match(pattern, v.replace(" ", "")):
            raise ValueError("Invalid Accept-Language format")
        return v
    
    class Config:
        populate_by_name = True


# Задание 5.1 - Login
class LoginRequest(BaseModel):
    username: str
    password: str


# Профиль пользователя
class UserProfile(BaseModel):
    username: str
    email: str
