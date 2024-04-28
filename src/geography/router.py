from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.geography.schemas import (CityDistrictsOut, DistrictCreateSchemas,
                                   DistrictShortViewSchemas,
                                   DistrictViewSchemas, GeographyCreateSchemas,
                                   GeographyViewSchemas)
from src.geography.service import district_service, geography_service
from src.users.perms import PermsRequired
from src.users.schemas import Permission

router = APIRouter(
    tags=["Geography"]
)


@router.get("/cities",
            status_code=status.HTTP_200_OK,
            response_model=List[GeographyViewSchemas],
            dependencies=[PermsRequired([Permission.VIEW_CITY])])
async def get_cities():
    return await geography_service.list_cities()


@router.post("/cities",
             status_code=status.HTTP_201_CREATED,
             dependencies=[PermsRequired([Permission.CREATE_CITY])],
             response_model=GeographyViewSchemas)
async def create_city(payload: GeographyCreateSchemas):
    return await geography_service.create(payload)


@router.get("/cities/{id}", status_code=status.HTTP_200_OK, response_model=GeographyViewSchemas)
async def get_city(id: int, db: AsyncSession = Depends(get_db)):
    return await geography_service.get_city(id, db)


@router.patch("/cities/{id}",
              status_code=status.HTTP_200_OK,
              dependencies=[PermsRequired([Permission.UPDATE_CITY])],
              response_model=GeographyViewSchemas)
async def update_city(id: int, payload: GeographyCreateSchemas, db: AsyncSession = Depends(get_db)):
    return await geography_service.update_city(id, payload, db)


@router.delete("/cities/{id}", status_code=status.HTTP_200_OK, dependencies=[PermsRequired([Permission.DELETE_CITY])])
async def delete_city(id: int, db: AsyncSession = Depends(get_db)):
    return await geography_service.delete_city(id, db)


@router.get("/districts/{city_id}", status_code=status.HTTP_200_OK, response_model=List[DistrictViewSchemas])
async def get_district(db: AsyncSession = Depends(get_db), city_id: int = None):
    return await district_service.get(city_id, db)


@router.get("/districts", status_code=status.HTTP_200_OK, response_model=DistrictViewSchemas)
async def get_districts(payload: DistrictCreateSchemas, db: AsyncSession = Depends(get_db)):
    return await district_service.get(payload, db)


@router.post("/districts",
             status_code=status.HTTP_201_CREATED,
             dependencies=[PermsRequired([Permission.CREATE_DISTRICT])],
             response_model=DistrictViewSchemas)
async def create_district(payload: DistrictCreateSchemas, db: AsyncSession = Depends(get_db)):
    return await district_service.create(payload, db)


@router.get("/districts/{id}", status_code=status.HTTP_200_OK, response_model=DistrictViewSchemas)
async def get_district(id: int, db: AsyncSession = Depends(get_db)):
    return await district_service.get_by_id(id, db)


@router.patch("/districts/{id}", status_code=status.HTTP_200_OK,
              dependencies=[PermsRequired([Permission.UPDATE_DISTRICT])])
async def update_district(id: int, payload: DistrictCreateSchemas, db: AsyncSession = Depends(get_db)):
    return await district_service.update_distict(id, payload, db)


@router.delete("/districts/{id}", status_code=status.HTTP_200_OK,
               dependencies=[PermsRequired([Permission.DELETE_DISTRICT])])
async def delete_district(id: int, db: AsyncSession = Depends(get_db)):
    return await district_service.delete_district(id, db)


@router.get("/cities_districts",
            status_code=status.HTTP_200_OK,
            response_model=List[CityDistrictsOut],
            dependencies=[PermsRequired([Permission.VIEW_CITY])])
async def get_cities_districts(db: AsyncSession = Depends(get_db)):
    return await district_service.get_cities_districts(db)
