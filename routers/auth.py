from datetime import timedelta
from typing import Annotated
from starlette import status
from fastapi import Depends, APIRouter, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import services, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]




@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: db_dependency):
    return services.create_user(db=db, user=user)


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = services.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")
    token = services.create_access_token(user.username, user.id, timedelta(minutes=30))
    return token

