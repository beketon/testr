import json
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, model_validator

from src.action_history.schemas import ActionHistoryShortOut
from src.directions.schemas import DirectionOut
from src.expenses.schemas import ExpenseViewSchemas
from src.geography.schemas import DistrictShortViewSchemas
from src.orders.models import DeliveryType, OrderStatus
from src.warehouse.schemas import WarehouseOutShort


class OrderItemsCreateSchemas(BaseModel):
    photo: str | None = None


class OrderPhotosOutSchemas(BaseModel):
    photo: str | None = None


class OrderItemsOut(OrderItemsCreateSchemas):
    id: int
    status: OrderStatus
    warehouse_id: int | None = None
    qr_code_hash: str | None = None
    fine: int = 0
    is_loaded: bool = False

    class Config:
        from_attributes = True


class PayerType(Enum):
    SENDER = "SENDER"
    RECEIVER = "RECEIVER"
    UL = "UL"


class PaymentType(Enum):
    CASH = "CASH"
    ONLINE = "ONLINE"


class Currency(Enum):
    KZT = "KZT"
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"


class PaymentUpdateSchemas(BaseModel):
    amount: float
    currency: Currency = Currency.KZT
    payment_type: PaymentType | None = None
    comment: str | None = ''
    payer_type: PayerType | None = None
    bin: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example":
            {
                "amount": 100.0,
                "currency": "KZT",
                "payment_type": "CASH",
                "comment": "Оплатит по прибытию груза",
                "payer_type": "SENDER",
                "bin": "123456789012"
            }
        }


class PaymentCreateSchemas(PaymentUpdateSchemas):
    ...


class PaymentOut(PaymentCreateSchemas):
    payment_status: str


class OrderItemsCreateSchemas(BaseModel):
    order_id: int
    qr_code_hash: str | None = None

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class OrderItemsViewSchemas(BaseModel):
    id: int
    order_id: int
    photo: str | None = None
    status: OrderStatus
    qr_code_hash: str | None = None

    class Config:
        from_attributes = True


class OrderUpdateSchemas(BaseModel):
    sender_address: str
    receiver_address: str | None = None
    description: str | None = None
    courier: int | None = None
    sender_fio: str
    sender_phone: str
    receiver_fio: str
    receiver_phone: str
    total_weight: float | None = None
    total_volume: float | None = None
    insurance: float | None = None
    warehouse_id: int | None = None
    district_id: int | None = None
    destination_warehouse_id: int | None = None
    direction_id: int
    payment: PaymentUpdateSchemas | None = None
    delivery_type: DeliveryType | None = None
    cargo_pickup_type: DeliveryType | None = None
    expenses: List | None = None
    expenses_price: float | None = None
    start_warehouse_id: int | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example":
            {
                "sender_address": "Almaty",
                "receiver_address": "Almaty",
                "description": "Some description",
                "courier": 1,
                "sender_fio": "John Doe",
                "sender_phone": "+77785547554",
                "receiver_fio": "John Doe",
                "receiver_phone": "+77785547554",
                "total_weight": 10.0,
                "total_volume": 10.0,
                "insurance": 10.0,
                "warehouse_id": 1,
                "district_id": 1,
                "destination_warehouse_id": 2,
                "direction_id": 1,
                "delivery_type": "DELIVERY",
                "cargo_pickup_type": "DELIVERY",
                "expenses": [1, 2, 3],
                "expenses_price": 100,
                "start_warehouse_id": 1,
                "payment": {
                    "amount": 100.0,
                    "currency": "KZT",
                    "payment_type": "CASH",
                    "comment": "Оплатит по прибытию груза",
                    "payer_type": "SENDER",
                    "bin": "123456789012"
                }
            }
        }


class OrdersCreateSchemas(BaseModel):
    sender_address: str
    receiver_address: str | None = None
    description: str | None = None
    courier: int | None = None
    sender_fio: str
    sender_phone: str
    receiver_fio: str
    receiver_phone: str
    total_weight: float | None = None
    total_volume: float | None = None
    insurance: float | None = None
    start_warehouse_id: int | None = None
    warehouse_id: int | None = None
    district_id: int | None = None
    direction_id: int
    destination_warehouse_id: int | None = None
    payment: PaymentCreateSchemas | None = None
    expenses: List | None = None
    delivery_type: DeliveryType | None = None
    cargo_pickup_type: DeliveryType | None = None
    expenses_price: float | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example":
            {
                "sender_address": "Almaty",
                "receiver_address": "Almaty",
                "courier": 1,
                "sender_fio": "John Doe",
                "sender_phone": "+77785547554",
                "receiver_fio": "John Doe",
                "description": "Some description",
                "receiver_phone": "+77785547554",
                "total_weight": 10.0,
                "total_volume": 10.0,
                "insurance": 10.0,
                "start_warehouse_id": 1,
                "warehouse_id": 1,
                "direction_id": 1,
                "district_id": 1,
                "delivery_type": "DELIVERY",
                "cargo_pickup_type": "DELIVERY",
                "payment": {
                    "amount": 100.0,
                    "currency": "KZT",
                    "comment": "Оплатит по прибытию груза",
                    "payment_type": "CASH",
                    "payer_type": "SENDER",
                    "bin": "123456789012"
                },
                "expenses_price": 200
            }
        }


class OrderViewShortSchemas(BaseModel):
    id: int
    created_at: datetime
    order_items: list[OrderItemsOut] | None = None
    sender_address: str
    receiver_address: str
    courier: int | None = None
    description: str | None = None
    not_delivered_reason: str | None = None
    cancellation_reason: str | None = None
    sender_fio: str
    sender_phone: str
    receiver_fio: str
    receiver_phone: str
    total_weight: float | None = None
    total_volume: float | None = None
    insurance: float | None = None
    direction: DirectionOut | None = None

    class Config:
        from_attributes = True


class OrderViewSchemas(BaseModel):
    id: int
    sender_address: str
    receiver_address: str
    courier: int | None = None
    description: str | None = None
    not_delivered_reason: str | None = None
    cancellation_reason: str | None = None
    sender_fio: str
    sender_phone: str
    receiver_fio: str
    receiver_phone: str
    total_weight: float | None = None
    total_volume: float | None = None
    insurance: float | None = None
    order_items_number: int
    created_at: datetime
    is_public_offer_accepted: bool | None = None
    order_status: OrderStatus
    delivery_type: DeliveryType | None = None
    cargo_pickup_type: DeliveryType
    public_offer_url: str | None = None
    direction: DirectionOut | None = None
    payment: PaymentOut | None = None
    start_warehouse: WarehouseOutShort | None = None
    warehouse: WarehouseOutShort | None = None
    destination_warehouse: WarehouseOutShort | None = None
    direction: DirectionOut | None = None
    expenses: List[ExpenseViewSchemas] = []
    action_histories: List[ActionHistoryShortOut] = []
    order_items: list[OrderItemsOut] | None = None
    district: DistrictShortViewSchemas | None = None
    waiver_agreement_url: str | None = None
    expenses_price: float | None = None
    is_payment_editable: bool = False
    order_photos: list[OrderPhotosOutSchemas] | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example":
            {
                "id": 1,
                "sender_address": "Almaty",
                "courier": 1,
                "description": "Some description",
                "sender_fio": "John Doe",
                "sender_phone": "+77785547554",
                "receiver_fio": "John Doe",
                "receiver_phone": "+77785547554",
                "total_weight": 10.0,
                "total_volume": 10.0,
                "insurance": 10.0,
                "order_items_number": 1,
                "created_at": "2021-06-29T16:00:00",
                "is_public_offer_accepted": True,
                "order_status": "NEW",
                "delivery_type": "DELIVERY",
                "cargo_pickup_type": "DELIVERY",
                "public_offer_url": "https://example.com",
                "direction": {
                    "id": 1,
                    "name": "Almaty - Nur-Sultan"
                },
                "payment": {
                    "amount": 100.0,
                    "currency": "KZT",
                    "payment_type": "CASH",
                    "payer_type": "SENDER",
                    "bin": "123456789012",
                    "payment_status": "PAID"
                },
                "start_warehouse": {
                    "id": 1,
                    "name": "Almaty"
                },
                "warehouse": {
                    "id": 1,
                    "name": "Almaty"
                },
                "destination_warehouse": {
                    "id": 2,
                    "name": "Nur-Sultan"
                },
                "expenses": [
                    {
                        "id": 1,
                        "amount": 100.0,
                        "description": "Some description",
                        "created_at": "2021-06-29T16:00:00"
                    }
                ],
                "action_histories": [
                    {
                        "id": 1,
                        "action_type": "CREATE",
                        "created_at": "2021-06-29T16:00:00"
                    }
                ],
                "order_items": [
                    {
                        "id": 1,
                        "order_id": 1,
                        "photo": "https://example.com",
                        "status": "NEW",
                        "qr_code_hash": "12345678901234567890123456789012"
                    }
                ]
            },
            "waiver_agreement_url": "https://example.com",
            "expenses_price": 100
        }


class OrderViewSchemasShort(BaseModel):
    id: int
    sender_address: str
    receiver_address: str
    sender_fio: str
    sender_phone: str
    receiver_fio: str
    receiver_phone: str
    order_items_number: int
    created_at: datetime
    order_status: OrderStatus
    direction: DirectionOut | None = None
    payment: PaymentOut | None = None
    warehouse: WarehouseOutShort | None = None


class OrderPaginated(BaseModel):
    page: int
    limit: int
    total: int
    pages_number: int
    data: list[OrderViewSchemasShort]


class OrderItemsPaginated(BaseModel):
    page: int
    limit: int
    total: int
    pages_number: int
    data: list[OrderItemsViewSchemas]


class SendOTPSigning(BaseModel):
    phone: str
    code: str


class SignOrderOTP(BaseModel):
    code: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example":
            {
                "code": "123456"
            }
        }


class CancelledOrder(BaseModel):
    reason: str

    model_config = {"from_attributes": True, "json_schema_extra": {"example": {
        "reason": "Груз не подходил по параметрам, не упакован, не готов к отправке"}}}


class NotDeliveredOrder(BaseModel):
    reason: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example":
            {
                "reason": "Не дозвонились до клиента"
            }
        }
    }


class ExpensesTotalPrice(BaseModel):
    expenses_total_price: float = 0.0


class TotalAmountOrder(BaseModel):
    total_volume: float = 0.0
    total_weight: float = 0.0
    expenses_price: float = 0.0
    direction_id: int
    cargo_pickup_type: str | None = None
    delivery_type: str | None = None


class TotalAmount(BaseModel):
    total_amount: float = 0.0


class CourierDeliverySchema(BaseModel):
    orders_items_id: List[int] = []

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "orders_items_id": [1, 2, 3]
            }
        }
    }

