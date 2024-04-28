from pydantic import BaseModel


class TransportationTypeBase(BaseModel):
    name: str
    is_active: bool = True

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "ROAD",
                "is_active": True
            }
        }
    }
