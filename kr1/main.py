from fastapi import FastAPI
from fastapi.responses import FileResponse
from models import User, UserWithAge, Feedback, FeedbackValidated
import os

app = FastAPI()

feedbacks = []

# Задание 1.2: GET "/" возвращает HTML файл
@app.get("/")
def read_html():
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(file_path, media_type="text/html")


# Задание 1.3: POST "/calculate" принимает два числа и возвращает их сумму
@app.post("/calculate")
def calculate(num1: float, num2: float):
    return {"result": num1 + num2}


# Задание 1.4: GET "/users" возвращает данные пользователя
@app.get("/users")
def get_user():
    user = User(name="Лилия Кандалова", id=1)
    return user


# Задание 1.5: POST "/user" принимает User с возрастом и возвращает с полем is_adult
@app.post("/user")
def check_user(user: UserWithAge):
    is_adult = user.age >= 18
    return {
        "name": user.name,
        "age": user.age,
        "is_adult": is_adult
    }


# Задание 2.1: POST "/feedback" сохраняет отзывы
@app.post("/feedback")
def submit_feedback(feedback: Feedback):
    feedbacks.append(feedback.dict())
    return {"message": f"Feedback received. Thank you, {feedback.name}."}


# Задание 2.2: POST "/feedback" с валидацией
@app.post("/feedback_validated")
def submit_feedback_validated(feedback: FeedbackValidated):
    feedbacks.append(feedback.dict())
    return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}
