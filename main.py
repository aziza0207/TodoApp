from fastapi import FastAPI
import models
from database import engine
from routers import todos, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(todos.router)
