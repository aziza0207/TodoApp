import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from main import app
from database import Base
from models import Todo
from routers.todos import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
                       poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()


app.dependency_overrides[get_db] = override_get_db
db = override_get_db()

client = TestClient(app)


@pytest.fixture()
def test_todo():
    todo = Todo(title="Test Todo",
                description="Description of Test Todo",
                is_complete=False,
                priority=1,
                owner_id=1
                )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todo;"))
        connection.commit()


def test_get_all_todos(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    # assert response.json()[0]["title"] == test_todo.title
    # assert response.json()[0]["id"] == test_todo.id
    # assert response.json()[0]["description"] == test_todo.description
