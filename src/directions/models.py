from enum import Enum

from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import relationship

from src.common.models import TimestampMixin
from src.database import Base


class TransportationType(str, Enum):
    AIR = "AIR"
    RAIL = "RAIL"
    ROAD = "ROAD"


class Directions(Base, TimestampMixin):
    __tablename__ = "directions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    arrival_city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    arrival_city = relationship(
        "City",
        back_populates="direction_arrival",
        foreign_keys=[arrival_city_id],
        lazy="selectin")
    departure_city_id = Column(
        Integer, ForeignKey("cities.id"), nullable=False)
    departure_city = relationship("City", back_populates="direction_departure",
                                  foreign_keys=[departure_city_id], lazy="selectin")
    is_active = Column(Boolean, default=True)
    transportation_type = Column(PgEnum(TransportationType), nullable=False)
    shipping = relationship("Shipping", back_populates="direction")
    user = relationship("Users", back_populates="direction")
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    order = relationship("Orders", backref="Orders.direction_id", primaryjoin='Directions.id==Orders.direction_id')

    __table_args__ = (
        UniqueConstraint(
            'arrival_city_id',
            'departure_city_id',
            'transportation_type',
            name='uq_transportation_type_arrival_departure_city'),
    )
