from datetime import datetime

from pydantic import BaseModel

from src.action_history.models import ActionCode


class ActionHistoryCreate(BaseModel):
    client_id: int | None = None
    courier_id: int | None = None
    manager_id: int | None = None
    warehouse_id: int | None = None
    warehouse_manager_id: int | None = None
    action_code: ActionCode
    order_item_id: int | None = None
    order_id: int | None = None


class ActionHistoryShortOut(BaseModel):
    created_at: datetime
    action_description: str
    action_code: ActionCode

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "created_at": "2021-09-16T10:54:13.000Z",
                "action_description": "Заказ создан",
                "action_code": "ORDER_CREATED"
            }
        }
    }


class SetOrderItemWarehouseStatus(BaseModel):
    warehouse_id: int
    order_item_id: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "warehouse_id": 1,
                "order_item_id": 2
            }
        }
    }
