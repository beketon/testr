from pydantic import BaseModel

from src.geography.schemas import (DistrictShortViewSchemas,
                                   GeographyViewSchemas)
from src.users.schemas import UserShortViewSchemas, UserViewSchemas


class WarehouseCreateSchemas(BaseModel):
    address: str
    name: str
    city: int
    district: int | None = None
    warehouse_user: int | None = None
    status: bool = True
    phone: str | None = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "address": "Almaty",
                "name": "Almaty",
                "city": 1,
                "phone": "+5555555555"
            }
        },
    }


class WarehouseUpdateSchemas(BaseModel):
    address: str | None = None
    name: str | None = None
    city: int | None = None
    district: int | None = None
    warehouse_user: int | None = None
    status: bool | None = None
    phone: str | None = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "address": "Almaty",
                "name": "Almaty",
                "city": 1,
                "district": 1,
                "status": True,
                "phone": "+5555555555"
            }
        },
    }


class WarehouseViewSchemas(BaseModel):
    id: int
    address: str
    name: str
    city: GeographyViewSchemas | None = None
    district: DistrictShortViewSchemas | None = None
    warehouse_user: UserShortViewSchemas | None = None
    orders_items_number: int
    status: bool
    phone: str | None = None
    orders_count: int

    class Config:
        from_attributes = True


class WarehouseOutShort(BaseModel):
    id: int
    name: str
    address: str

    class Config:
        from_attributes = True
