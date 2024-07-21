import jwt
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "4542afb3620912169ccc155eab98f4c9f2b8d95799bd2b1763468545481cc15a"
ALGORITHM = "HS256"


def authenticate_user(username: str, password: str, db):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {
        "sub": username,
        "id": user_id
    }
    expire = datetime.utcnow() + expires_delta
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password),
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
