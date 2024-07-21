from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    first_name: str
    username :str
    last_name: str
    email: str
    password: str

