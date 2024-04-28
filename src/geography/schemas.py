from typing import List

from pydantic import BaseModel


class GeographyCreateSchemas(BaseModel):
    name: str


class GeographyViewSchemas(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CityOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class DistrictShortViewSchemas(BaseModel):
    id: int
    name: str
    city: int | None = None

    class Config:
        from_attributes = True


class DistrictViewSchemas(BaseModel):
    id: int
    name: str
    city: GeographyViewSchemas

    class Config:
        from_attributes = True


class DistrictUpdateSchemas(BaseModel):
    name: str
    city: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "name": "Бостандыкский",
                "city": 1
            }
        },
    }


class DistrictCreateSchemas(DistrictUpdateSchemas):
    ...

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "name": "Бостандыкский",
                "city": 1
            }
        },
    }


class CityDistrictsOut(BaseModel):
    id: int
    name: str
    districts: List[DistrictShortViewSchemas]
