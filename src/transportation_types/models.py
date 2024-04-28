from sqlalchemy import Boolean, Column, Integer, String

from src.common.models import TimestampMixin
from src.database import Base


class TransportationTypeDB(Base, TimestampMixin):
    __tablename__ = "transportation_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
