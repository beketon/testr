from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from sqlalchemy import Column, DateTime


class TimestampMixin(object):
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class SendEmail(BaseModel):
    email: str
    subject: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "zshanabek@gmail.com",
                "subject": "Hello",
                "message": "Hello world"
            }
        }


class SortOrder(Enum):
    ASC = "asc"
    DESC = "desc"
