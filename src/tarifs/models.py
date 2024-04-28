from enum import Enum

from sqlalchemy import Column, Float, ForeignKey, Integer, UniqueConstraint, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from src.database import Base


class CalculationType(str, Enum):
    VOLUME = "VOLUME"
    WEIGHT = "WEIGHT"
    HANDLING = "HANDLING"
    DELIVERY_WEIGHT = "DELIVERY_WEIGHT"
    DELIVERY_VOLUME = "DELIVERY_VOLUME"
    SENDER_CARGO_PICKUP_VOLUME = "SENDER_CARGO_PICKUP_VOLUME"
    SENDER_CARGO_PICKUP_WEIGHT = "SENDER_CARGO_PICKUP_WEIGHT"


class Tarifs(Base):
    __tablename__ = "tarifs"

    id = Column(Integer, primary_key=True, index=True)
    calculation_type = Column(PgEnum(CalculationType), nullable=False)
    direction_id = Column(Integer, ForeignKey("directions.id"), nullable=True)
    amount = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    is_limit = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint(
            'calculation_type',
            'direction_id',
            'amount',
            name='idx_tarifs_calculation_type_direction_id_amount'),
    )
