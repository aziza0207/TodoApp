from sqlalchemy.orm import Session
import models, schemas


def get_todo(db: Session, todo_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()


def create_todo(db: Session, todo: schemas.TodoBase, owner_id):
    db_todo = models.Todo(
        title=todo.title,
        description=todo.description,
        is_complete=todo.is_complete,
        priority=todo.priority,
        owner_id=owner_id

    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def update_todo(db: Session, todo_id: int, todo):
    db_todo = get_todo(db=db, todo_id=todo_id)
    db_todo.title = todo.title
    db_todo.description = todo.description
    db_todo.is_complete = todo.is_complete
    db_todo.priority = todo.priority
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo
