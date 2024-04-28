import random
from datetime import datetime
from enum import Enum

from sqlalchemy import (DECIMAL, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, text, select)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import relationship

from src.common.models import TimestampMixin
from src.database import Base
from src.expenses.models import order_expenses
from src.shipping.models import (shipping_order_association,
                                 shipping_order_items_association)
from src.users.perms import if_user_has_permissions
from src.users.schemas import Permission


class OrderStatus(Enum):
    CREATED = "CREATED"
    ASSIGNED_TO_COURIER = "ASSIGNED_TO_COURIER"
    COURIER_DELIVERING_TO_WAREHOUSE = "COURIER_DELIVERING_TO_WAREHOUSE"
    ACCEPTED_TO_WAREHOUSE = "ACCEPTED_TO_WAREHOUSE"
    CLIENT_DELIVERING_TO_WAREHOUSE = "CLIENT_DELIVERING_TO_WAREHOUSE"
    IN_TRANSIT = "IN_TRANSIT"
    PARTIALLY_IN_TRANSIT = "PARTIALLY_IN_TRANSIT"
    ARRIVED_TO_DESTINATION = "ARRIVED_TO_DESTINATION"
    DELIVERING_TO_RECIPIENT = "DELIVERING_TO_RECIPIENT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    NOT_DELIVERED = "NOT_DELIVERED"


class DeliveryType(Enum):
    DELIVERY = "DELIVERY"
    PICKUP = "PICKUP"


STATUS_GROUPS = {
    "NOT_DELIVERED": [
        OrderStatus.NOT_DELIVERED],
    "PENDING": [
        OrderStatus.ASSIGNED_TO_COURIER,
        OrderStatus.COURIER_DELIVERING_TO_WAREHOUSE,
        OrderStatus.ACCEPTED_TO_WAREHOUSE,
        OrderStatus.CLIENT_DELIVERING_TO_WAREHOUSE,
        OrderStatus.IN_TRANSIT,
        OrderStatus.PARTIALLY_IN_TRANSIT,
        OrderStatus.ARRIVED_TO_DESTINATION,
        OrderStatus.DELIVERING_TO_RECIPIENT],
    "DELIVERED": [
        OrderStatus.DELIVERED],
    "CANCELLED": [
        OrderStatus.CANCELLED],
    "LEADS": [
        OrderStatus.CREATED]}


class PaymentStatus(Enum):
    NOT_PAID = "NOT_PAID"
    PAID = "PAID"


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    currency = Column(String, nullable=False)
    payment_status = Column(String, nullable=False)
    payment_type = Column(String, nullable=True)
    payer_type = Column(String, nullable=True)
    bin = Column(String, nullable=False)
    payment_date = Column(DateTime, default=datetime.now)
    order = relationship("Orders", back_populates="payment")


class Orders(Base, TimestampMixin):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, nullable=False)
    creator = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    sender_address = Column(String, nullable=False)
    receiver_address = Column(String, nullable=False)
    courier = Column(Integer, ForeignKey("users.id"), nullable=True)
    sender_fio = Column(String, nullable=False)
    sender_phone = Column(String, nullable=False)
    receiver_fio = Column(String, nullable=False)
    receiver_phone = Column(String, nullable=False)
    order_status = Column(String, nullable=False)
    order_status_previous = Column(String, nullable=True)
    payment = relationship("Payment", uselist=False, back_populates="order")
    delivery_type = Column(String, nullable=True, server_default="DELIVERY")
    cargo_pickup_type = Column(
        PgEnum(DeliveryType), nullable=True, server_default=DeliveryType.PICKUP.value)
    insurance = Column(DECIMAL(10, 2), nullable=True)
    total_weight = Column(Float, nullable=True)
    total_volume = Column(Float, nullable=True)
    not_delivered_reason = Column(String, nullable=True)
    cancellation_reason = Column(String, nullable=True)
    start_warehouse_id = Column(
        Integer, ForeignKey("warehouses.id"), nullable=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    destination_warehouse_id = Column(
        Integer, ForeignKey("warehouses.id"), nullable=True)
    direction_id = Column(Integer, ForeignKey("directions.id"))
    district_id = Column(Integer, ForeignKey("districts.id"))
    description = Column(String, nullable=True)
    public_offer_url = Column(String, nullable=True)
    is_public_offer_accepted = Column(Boolean, server_default=text('false'))
    is_waiver_agreement_accepted = Column(
        Boolean, server_default=text('false'))
    expenses = relationship(
        "Expense", secondary=order_expenses, back_populates="orders", lazy="selectin")
    order_items = relationship(
        "OrderItems", back_populates="order", lazy="selectin")
    shippings = relationship("Shipping", secondary=shipping_order_association,
                             back_populates="orders", lazy="selectin")
    warehouse = relationship(
        "Warehouse", back_populates="order", foreign_keys="Orders.warehouse_id")
    direction = relationship(
        "Directions", back_populates="order", foreign_keys="Orders.direction_id")
    waiver_agreement_url = Column(String, nullable=True)
    expenses_price = Column(Float, nullable=True)
    order_photo = relationship(
        "OrderPhoto", back_populates="order", lazy="selectin")
    users = relationship("UsersOrders", back_populates="order")

    def is_payment_editable(self, user, db):
        return if_user_has_permissions(db, user.id, [Permission.UPDATE_PAYMENT_STATUS_UL])

    @staticmethod
    async def generate_unique_id(db):
        while True:
            potential_id = random.randint(100000, 999999)
            stmt = select(Orders).where(Orders.id == potential_id)
            result = await db.execute(stmt)
            if result.scalar() is None:
                return potential_id


class OrderItems(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order = relationship(
        "Orders", back_populates="order_items", lazy="selectin")
    photo = Column(String, nullable=True)
    status = Column(String, nullable=False)
    qr_code_hash = Column(String, nullable=True, unique=True)
    shippings = relationship("Shipping", secondary=shipping_order_items_association,
                             back_populates="order_items", lazy="selectin")
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    is_loaded = Column(Boolean, server_default=text('false'))


class OrderPhoto(Base):
    __tablename__ = "order_photo"
    id = Column(Integer, primary_key=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order = relationship(
        "Orders", back_populates="order_photo", lazy="selectin")
    photo = Column(String, nullable=True)
