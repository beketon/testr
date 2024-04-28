from datetime import date

from pydantic import BaseModel

from src.directions.models import TransportationType
from src.orders.models import OrderStatus
from src.orders.schemas import PaymentType


class TotalWeightSchema(BaseModel):
    total_weight: float


class TotalVolume(BaseModel):
    total_volume: float


class TotalOrdersCount(BaseModel):
    total_orders_count: int


class OrdersStatistics(BaseModel):
    status: str
    count: int


class ShippingTypeCount(BaseModel):
    shipping_type: TransportationType
    count: int


class ShippingStatistics(BaseModel):
    shipping_types: list[ShippingTypeCount]
    created_at: date


class PaymentStatistics(BaseModel):
    payment_type: PaymentType
    count: int


ORDER_GROUPS = {
    "NOT_DELIVERED": [
        OrderStatus.NOT_DELIVERED.value,
    ],
    "PENDING": [
        OrderStatus.ASSIGNED_TO_COURIER.value,
        OrderStatus.COURIER_DELIVERING_TO_WAREHOUSE.value,
        OrderStatus.ACCEPTED_TO_WAREHOUSE.value,
        OrderStatus.CLIENT_DELIVERING_TO_WAREHOUSE.value,
        OrderStatus.IN_TRANSIT.value,
        OrderStatus.ARRIVED_TO_DESTINATION.value,
        OrderStatus.DELIVERING_TO_RECIPIENT.value],
    "DELIVERED": [
        OrderStatus.DELIVERED.value,
    ],
    "CANCELLED": [
        OrderStatus.CANCELLED.value,
    ],
    "LEADS": [
        OrderStatus.CREATED.value,
    ]}


class CourierStatisticsSchema(BaseModel):
    user_id: int
    courier_name: str | None = None
    selected_orders: int | None = None
    total_profit: float | None = None
    delivered_orders: int | None = None
