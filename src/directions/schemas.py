from pydantic import BaseModel

from src.directions.models import TransportationType
from src.geography.schemas import CityOut, GeographyViewSchemas


class DirectionCreateSchemas(BaseModel):
    arrival_city_id: int
    departure_city_id: int
    is_active: bool = True
    transportation_type: TransportationType
    email: str
    password: str

    model_config = {
        "json_schema_extra": {
            "example":
            {
                "arrival_city_id": 1,
                "departure_city_id": 2,
                "transportation_type": "RAIL",
                "email": "dope.coder3@gmail.com",
                "password": "ff3d3ff4f4"
            }
        }
    }


class DirectionUpdateSchemas(BaseModel):
    arrival_city_id: int | None
    departure_city_id: int | None
    is_active: bool | None
    transportation_type: TransportationType | None
    email: str | None
    password: str | None

    model_config = {
        "json_schema_extra": {
            "example":
            {
                "arrival_city_id": 1,
                "departure_city_id": 2,
                "is_active": True,
                "transportation_type": "RAIL",
                "email": "dope.coder3@gmail.com",
                "password": "ff3d3ff4f4"
            }
        }
    }


class DirectionViewSchemas(BaseModel):
    id: int
    arrival_city: GeographyViewSchemas
    departure_city: GeographyViewSchemas
    is_active: bool
    transportation_type: TransportationType
    email: str | None = None
    password: str | None = None

    class Config:
        from_attributes = True


class DirectionOut(BaseModel):
    id: int
    arrival_city: CityOut
    departure_city: CityOut
    transportation_type: TransportationType

    class Config:
        from_attributes = True
