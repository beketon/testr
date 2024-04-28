from enum import Enum

from sqlalchemy import (DECIMAL, Boolean, Column, Date, DateTime, Float,
                        ForeignKey, Integer, String, Table, text)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import relationship

from src.common.models import TimestampMixin
from src.database import Base
from src.directions.models import TransportationType


class ShippingStatus(str, Enum):
    FINISHED = "FINISHED"
    IN_TRANSIT = "IN_TRANSIT"
    NEW = "NEW"
    WAITING_DRIVER = "WAITING_DRIVER"
    CANCELED = "CANCELED"


class ShippingRespondStatus(str, Enum):
    CANCEL = "CANCEL"
    FINISHED = "FINISHED"
    CONFIRMED = "CONFIRMED"
    RESPONDED = "RESPONDED"


shipping_order_items_association = Table(
    "shipping_order_items",
    Base.metadata,
    Column("shipping_id", Integer, ForeignKey("shipping.id")),
    Column("order_item_id", Integer, ForeignKey("order_items.id"))
)

shipping_order_association = Table(
    "shipping_order",
    Base.metadata,
    Column("shipping_id", Integer, ForeignKey("shipping.id")),
    Column("order_id", Integer, ForeignKey("orders.id"))
)


class ShippingWarehouse(Base):
    __tablename__ = "shipping_warehouse"
    shipping_id = Column(Integer, ForeignKey("shipping.id"), primary_key=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), primary_key=True)
    is_visited = Column(Boolean, server_default=text('false'))
    shipping = relationship("Shipping", back_populates="warehouses")
    warehouse = relationship("Warehouse", back_populates="shippings")


class ShippingRespond(Base, TimestampMixin):
    __tablename__ = "shipping_responds"
    id = Column(Integer, primary_key=True, nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"))
    shipping_id = Column(Integer, ForeignKey("shipping.id"))
    shipping = relationship(
        "Shipping",
        back_populates="respond",
        lazy="selectin",
        foreign_keys=[shipping_id])
    driver = relationship(
        "Users",
        back_populates="shipping_driver",
        lazy="selectin",
        foreign_keys=[driver_id])
    respond_status = Column(PgEnum(ShippingRespondStatus), nullable=True)


class Shipping(Base, TimestampMixin):
    __tablename__ = "shipping"
    id = Column(Integer, primary_key=True, nullable=False)
    price = Column(DECIMAL(9, 2), nullable=False)
    address = Column(String, nullable=True)
    cargo_weight = Column(Float, nullable=True)
    cargo_volume = Column(Float, nullable=True)
    status = Column(PgEnum(ShippingStatus), nullable=False)
    shipping_type = Column(PgEnum(TransportationType), nullable=False)
    number_train = Column(String, nullable=True)
    number_air = Column(String, nullable=True)
    count = Column(Integer, nullable=True)
    respond = relationship(
        "ShippingRespond",
        back_populates="shipping",
        foreign_keys=ShippingRespond.shipping_id)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    driver = relationship(
        "Users",
        back_populates="shipping",
        foreign_keys=[driver_id],
        lazy="selectin")
    departure_date = Column(DateTime)
    arrival_date = Column(DateTime, nullable=True)
    is_driver_contract_accepted = Column(Boolean, server_default=text('false'))
    direction_id = Column(Integer, ForeignKey("directions.id"), nullable=True)
    direction = relationship(
        "Directions", back_populates="shipping", lazy="selectin")
    warehouses = relationship("ShippingWarehouse", back_populates="shipping")
    order_items = relationship(
        "OrderItems",
        secondary=shipping_order_items_association,
        back_populates="shippings",
        lazy="selectin")
    orders = relationship(
        "Orders",
        secondary=shipping_order_association,
        back_populates="shippings",
        lazy="selectin")
    days = Column(Integer, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    start_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    end_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    start_warehouse = relationship(
        "Warehouse", back_populates="start_shipping",
        lazy="selectin",
        foreign_keys=[start_warehouse_id]
    )
    end_warehouse = relationship(
        "Warehouse",
        back_populates="end_shipping",
        lazy="selectin",
        foreign_keys=[end_warehouse_id]
    )
    invoice_number = Column(String, nullable=True)
    driver_contract_url = Column(String, nullable=True)
    is_loaded = Column(Boolean, server_default=text('false'))
