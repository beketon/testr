from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.common.models import TimestampMixin
from src.database import Base
from src.shipping.models import Shipping
from src.directions.models import Directions


class District(Base, TimestampMixin):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    city = relationship("City", uselist=False)
   
class City(Base, TimestampMixin):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    direction_departure = relationship("Directions", back_populates="departure_city", foreign_keys=Directions.departure_city_id)
    direction_arrival = relationship("Directions", back_populates="arrival_city", foreign_keys=Directions.arrival_city_id)