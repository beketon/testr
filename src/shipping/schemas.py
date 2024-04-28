from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field, validator

from src.directions.models import TransportationType
from src.directions.schemas import DirectionViewSchemas
from src.orders.schemas import OrderItemsViewSchemas, OrderViewShortSchemas
from src.users.schemas import UserShippingViewSchemas
from src.warehouse.schemas import WarehouseOutShort


class ShippingCoordinate(BaseModel):
    latitude: float
    longitude: float


class ShippingViewSchema(BaseModel):
    id: int
    price: float
    address: str | None = ""
    cargo_weight: float | None = 0
    cargo_volume: float | None = 0
    status: str
    shipping_type: TransportationType
    number_train: str | None = None
    number_air: str | None = None
    count: int | None = None
    departure_date: datetime | None = None
    created_at: datetime
    arrival_date: datetime | None = None
    driver_id: int | None = None
    driver: UserShippingViewSchemas | None = None
    is_driver_contract_accepted: bool | None = None
    warehouses: List[WarehouseOutShort] | None = None
    is_responded: bool | None = None
    is_accepted: bool | None = None
    is_canceled: bool | None = None
    direction: DirectionViewSchemas | None = None
    orders: List[OrderViewShortSchemas] | None = []
    order_items: List[OrderItemsViewSchemas] | None = []
    days: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    start_warehouse: WarehouseOutShort | None = None
    end_warehouse: WarehouseOutShort | None = None
    is_loaded: bool | None = None
    driver_contract_url: str | None = None
    order_items_count: int | None = None
    count_total_weight: int | None = None

    class Config:
        from_attributes = True


class PaginationShipping(BaseModel):
    page: int
    limit: int
    total: int
    pages_number: int
    data: list[ShippingViewSchema]


class ShippingCreateSchema(BaseModel):
    price: float = 0
    address: str | None = None
    cargo_weight: float | None = None
    cargo_volume: float | None = None
    shipping_type: TransportationType
    number_train: str | None = None
    number_air: str | None = None
    count: int | None = None
    departure_date: datetime | None = None
    direction_id: int
    warehouses_id: List[int] | None = None
    start_warehouse_id: int | None = None
    end_warehouse_id: int | None = None
    days: float | None = None
    invoice_number: str | None = None
    arrival_date: datetime | None = None

    @validator('price')
    def price_must_be_positive(cls, value):
        if value < 0:
            raise ValueError('price must be a positive value')
        return value


class ShippingPathSchema(BaseModel):
    price: float | None = None
    address: str | None = None
    cargo_weight: float | None = None
    cargo_volume: float | None = None
    status: str | None = None
    shipping_type: TransportationType | None = None
    departure_date: date | None = None
    arrival_date: date | None = None
    direction_id: int
    warehouses_id: List[int] | None = None
    start_warehouse_id: int | None = None
    end_warehouse_id: int | None = None
    days: float | None = None


class ShippingAddDriverCreateSchema(BaseModel):
    drivers: List[int] = Field(max_length=1, min_length=1)


class ShippingRespondViewSchema(BaseModel):
    id: int
    driver: UserShippingViewSchemas | None = None
    shipping: ShippingViewSchema | None = None
    respond_status: str | None = None

    class Config:
        from_attributes = True


class ShippingRespondCreateSchema(BaseModel):
    shipping_id: int


class ShippingLoadsSchema(BaseModel):
    orders_items_id: List[int] = []


class CourierShippingsSchema(BaseModel):
    id: int
    name: str | None = None
    order_count: int = 0


class CourierShippingsDetailSchema(BaseModel):
    id: int
    name: str | None = None
    orders: List[OrderViewShortSchemas] | None = []


class PaginationCourierShippings(BaseModel):
    page: int
    limit: int
    total: int
    pages_number: int
    data: list[CourierShippingsSchema]
