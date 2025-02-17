from typing import Annotated
from starlette import status
from fastapi import Depends, APIRouter, HTTPException, Path
from sqlalchemy.orm import Session
import services, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/todos", tags=["Todo"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(services.get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_todos(
    user: user_dependency, db: db_dependency, skip: int = 0, limit: int = 20
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return (
        db.query(models.Todo)
        .filter(models.Todo.owner_id == user.get("id"))
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, todo: schemas.TodoBase, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return services.create_todo(db=db, todo=todo, owner_id=user.get("id"))


@router.get("/{todo_id}/", status_code=status.HTTP_200_OK)
async def get_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    db_todo = services.get_todo(db, user.get("id"), todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo


@router.patch("/{todo_id}/", status_code=status.HTTP_200_OK)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo: schemas.TodoBase,
    todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    db_todo = services.get_todo(db, todo_id, user.get("id"))
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!")
    return services.update_todo(db=db, todo_id=todo_id, todo=todo, user_id=user.get("id"))


@router.delete("/{todo_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo( user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    db_todo = services.get_todo(db, user.get("id"), todo_id)
    if db_todo is None:
        HTTPException(status_code=404, detail="Todo not found!")
    db.delete(db_todo)
    db.commit()
