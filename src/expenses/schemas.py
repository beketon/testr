from pydantic import BaseModel

from src.users.schemas import UserShortViewSchemas 

class ExpenseCreateSchemas(BaseModel):
    name: str
    price: float

class ExpensePathSchemas(BaseModel):
    name: str | None = None
    price: float | None = None


class ExpenseViewSchemas(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True

