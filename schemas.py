from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0)
    is_complete: bool


class Todo(TodoBase):
    id: int

    class Config:
        from_attributes = True
