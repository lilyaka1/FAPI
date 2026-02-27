from pydantic import BaseModel, field_validator
from typing import Optional


class User(BaseModel):
    name: str
    id: int


class UserWithAge(BaseModel):
    name: str
    age: int


class Feedback(BaseModel):
    name: str
    message: str


class FeedbackValidated(BaseModel):
    name: str
    message: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if len(v) < 2 or len(v) > 50:
            raise ValueError("Name must be between 2 and 50 characters")
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        if len(v) < 10 or len(v) > 500:
            raise ValueError("Message must be between 10 and 500 characters")

        forbidden_words = ["кринж", "рофл", "вайб"]
        message_lower = v.lower()

        for word in forbidden_words:
            if word in message_lower:
                raise ValueError("Использование недопустимых слов")

        return v
