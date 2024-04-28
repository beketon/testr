from pydantic import BaseModel, confloat, conint

from src.tarifs.models import CalculationType


class TarifCreateSchemas(BaseModel):
    calculation_type: CalculationType
    starting_amount: conint(ge=0)
    ending_amount: conint(ge=0)
    starting_price: confloat(ge=0)
    increment: confloat(ge=0)
    direction_id: int | None = None

    model_config = {
        "json_schema_extra": {
            "example":
            {
                "calculation_type": "VOLUME",
                "starting_amount": 1,
                "ending_amount": 5,
                "starting_price": 500.0,
                "increment": 1000.0,
                "direction_id": 2
            }
        }
    }


class DeliveryTarifSchemas(BaseModel):
    calculation_type: CalculationType
    starting_amount: conint(ge=0)
    ending_amount: conint(ge=0)
    price: confloat(ge=0)
    direction_id: int | None = None

    model_config = {
        "json_schema_extra": {
            "example":
            {
                "calculation_type": "DELIVERY_WEIGHT",
                "starting_amount": 1,
                "ending_amount": 5,
                "price": 500.0,
                "direction_id": 2
            }
        }
    }


class TarifLimitListSchemas(BaseModel):
    calculation_type: CalculationType
    direction_id: int | None = None

    model_config = {
        "json_schema_extra": {
            "example":
            {
                "calculation_type": "VOLUME",
                "direction_id": 2
            }
        }
    }


class TarifLimitSchemas(BaseModel):
    calculation_type: CalculationType
    price: conint(ge=0)
    direction_id: int | None = None

    model_config = {
        "json_schema_extra": {
            "example":
            {
                "calculation_type": "VOLUME",
                "price": 500.0,
                "direction_id": 2
            }
        }
    }


class TarifUpdateSchemas(BaseModel):
    id: int
    price: confloat(ge=0.0)

    model_config = {
        "json_schema_extra": {
            "example":
            {
                "id": 1,
                "price": 500.0,
            }
        }
    }


class TarifViewSchemas(BaseModel):
    id: int
    amount: int
    price: float

    class Config:
        from_attributes = True
