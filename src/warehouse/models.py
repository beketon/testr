from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.common.models import TimestampMixin
from src.database import Base
from src.shipping.models import Shipping


class Warehouse(Base, TimestampMixin):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, nullable=False)
    address = Column(String, nullable=False)
    name = Column(String, nullable=False)
    city = Column(Integer, ForeignKey("cities.id"), nullable=False)
    district = Column(Integer, ForeignKey("districts.id"), nullable=True)
    warehouse_user = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Boolean, server_default="false")
    shippings = relationship("ShippingWarehouse", back_populates="warehouse")
    start_shipping = relationship("Shipping", back_populates="start_warehouse",
                                  foreign_keys=Shipping.start_warehouse_id)
    end_shipping = relationship("Shipping", back_populates="end_warehouse", foreign_keys=Shipping.end_warehouse_id)
    order = relationship("Orders", backref="Orders.warehouse_id", primaryjoin='Warehouse.id==Orders.warehouse_id')
    phone = Column(String, nullable=True)
