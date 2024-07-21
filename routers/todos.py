from typing import Annotated
from starlette import status
from fastapi import Depends, APIRouter, HTTPException, Path
from sqlalchemy.orm import Session
import services, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api/todos", tags=["Todo"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[schemas.Todo], status_code=status.HTTP_200_OK)
async def get_todos(db: db_dependency, skip: int = 0, limit: int = 20):
    return db.query(models.Todo).offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.TodoBase, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: schemas.TodoBase, db: db_dependency):
    return services.create_todo(db=db, todo=todo)


@router.get("/{todo_id}/", response_model=schemas.Todo, status_code=status.HTTP_200_OK)
async def get_product(db: db_dependency, todo_id: int = Path(gt=0)):
    db_todo = services.get_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo


@router.patch("/{todo_id}/", status_code=status.HTTP_200_OK)
async def update_todo(db: db_dependency, todo: schemas.TodoBase, todo_id: int = Path(gt=0)):
    db_todo = services.get_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!")
    return services.update_todo(db=db, todo_id=todo_id, todo=todo)


@router.delete("/{todo_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(db: db_dependency, todo_id: int = Path(gt=0)):
    db_todo = services.get_todo(db, todo_id=todo_id)
    if db_todo is None:
        HTTPException(status_code=404, detail="Todo not found!")
    db.delete(db_todo)
    db.commit()
