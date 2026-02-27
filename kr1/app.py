from fastapi import FastAPI

application = FastAPI()


@application.get("/")
def read_root():
    return {"message": "оно работает"}
