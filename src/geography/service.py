from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDao
from src.database import get_db
from src.geography.models import City, District
from src.geography.schemas import (CityDistrictsOut, DistrictCreateSchemas,
                                   DistrictShortViewSchemas,
                                   DistrictUpdateSchemas, DistrictViewSchemas,
                                   GeographyCreateSchemas,
                                   GeographyViewSchemas)


class GeographyService(BaseDao):
    class_name = City

    async def create(self, payload: GeographyCreateSchemas) -> dict:
        return await GeographyService.add({"name": payload.name})

    async def create_with_list(self, payload: list):
        return await GeographyService.add_all(payload)

    async def list_cities(self):
        return await GeographyService.all()

    async def get_city(self, id: int, db: AsyncSession = Depends(get_db)) -> GeographyViewSchemas:
        city = select(City).where(City.id == id)
        city = await db.execute(city)
        city = city.scalar_one_or_none()
        if city:
            return GeographyViewSchemas(**city.__dict__)
        raise HTTPException(status_code=404, detail="City not found")

    async def delete_city(self, id: int, db: AsyncSession = Depends(get_db)):
        city = select(City).where(City.id == id)
        city = await db.execute(city)
        city = city.scalar_one_or_none()
        if city:
            await db.delete(city)
            await db.commit()
            return {"detail": "City deleted"}
        raise HTTPException(status_code=404, detail="City not found")

    async def update_city(self, id: int, payload: GeographyCreateSchemas, db: AsyncSession = Depends(get_db)) -> GeographyViewSchemas:
        city = select(City).where(City.id == id)
        city = await db.execute(city)
        city = city.scalar_one_or_none()
        if city:
            city.name = payload.name
            await db.commit()
            return GeographyViewSchemas(**city.__dict__)
        raise HTTPException(status_code=404, detail="City not found")


class GeographyDistrictService(BaseDao):
    class_name = District

    async def create(self, payload: DistrictCreateSchemas, db: AsyncSession = Depends(get_db)) -> DistrictViewSchemas:
        district_data = await GeographyDistrictService.add({"name": payload.name, "city_id": payload.city})

        city_query = await db.execute(select(City).where(City.id == district_data.city_id))
        city = city_query.scalar_one_or_none()
        city_model = GeographyViewSchemas(**city.__dict__)

        district_model = DistrictViewSchemas(
            id=district_data.id,
            name=district_data.name,
            city=city_model
        )
        return district_model

    async def get(self, city_id: int, db: AsyncSession = Depends(get_db)) -> List[DistrictViewSchemas]:
        disctricts = await GeographyDistrictService.find_all({"city_id": city_id})
        resp = []
        for district in disctricts:
            city_query = await db.execute(select(City).where(City.id == district.city_id))
            city = city_query.scalar_one_or_none()
            city_model = GeographyViewSchemas(**city.__dict__)
            disctrict_data = DistrictViewSchemas(
                **district.__dict__, city=city_model)
            resp.append(disctrict_data)
        return resp

    async def get_by_id(self, id: int, db: AsyncSession = Depends(get_db)) -> DistrictViewSchemas:
        district = await GeographyDistrictService.find_by_id(id)
        city_query = await db.execute(select(City).where(City.id == district.city_id))
        city = city_query.scalar_one_or_none()
        city_model = GeographyViewSchemas(**city.__dict__)
        disctrict_data = DistrictViewSchemas(
            **district.__dict__, city=city_model)
        return disctrict_data

    async def get_cities_districts(self, db: AsyncSession = Depends(get_db)) -> List[CityDistrictsOut]:
        cities = await GeographyService.all()
        resp = []
        for city in cities:
            disctricts = await GeographyDistrictService.find_all({"city_id": city.id})
            disctricts_data = []
            for district in disctricts:
                disctricts_data.append(DistrictShortViewSchemas(
                    **district.__dict__, city=city.id))
            city_data = CityDistrictsOut(
                id=city.id, name=city.name, districts=disctricts_data)
            resp.append(city_data)
        return resp

    async def update_distict(self, id: int, payload: DistrictUpdateSchemas, db: AsyncSession = Depends(get_db)):
        district = select(District).where(District.id == id)
        district = await db.execute(district)
        district = district.scalar_one_or_none()
        if district:
            district.name = payload.name
            district.city_id = payload.city
            await db.commit()
            return district
        raise HTTPException(status_code=404, detail="District not found")


    async def delete_district(self, id: int, db: AsyncSession = Depends(get_db)):
        district = await GeographyDistrictService.find_by_id(id)
        if district:
            await db.delete(district)
            await db.commit()
            return {"detail": "District deleted"}
        raise HTTPException(status_code=404, detail="District not found")


district_service = GeographyDistrictService()
geography_service = GeographyService()