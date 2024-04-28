import json
import os

from sqlalchemy import and_, insert, select
from sqlalchemy.orm.exc import NoResultFound

from src.config import settings
from src.constants import Environment
from src.database import async_session
from src.geography.exceptions import JsonNotFound
from src.geography.models import City
from src.geography.schemas import DistrictCreateSchemas, GeographyCreateSchemas
from src.geography.service import district_service, geography_service
from src.users.models import Group, Permission, auth_group_permission
from src.users.schemas import (GROUP_LOCALISATION, PERMISSIONS_MAP,
                               RUSSIAN_PERMISSIONS_MAP)
from src.warehouse.schemas import WarehouseCreateSchemas
from src.warehouse.service import warehouse_service


async def init_data():
    await create_cities()
    await create_groups_and_permissions()


async def create_cities() -> None:
    if settings.ENVIRONMENT == Environment.LOCAL:
        return
    print("Creating cities, districts and warehouses")
    file_path = "src/geography/cities.json"
    db = async_session()
    if not os.path.exists(file_path):
        print("File not found")
        raise JsonNotFound()
    with open(file_path, "r") as file:
        cities_data = json.load(file)
    for city_data in cities_data:
        city = await db.execute(select(City).where(City.name == city_data["name"]))
        city = city.scalar_one_or_none()
        if city:
            continue
        city = await geography_service.create(GeographyCreateSchemas(name=city_data["name"]))
        for district in city_data["districts"]:
            district = await district_service.create(DistrictCreateSchemas(name=district["name"], city=city.id), db=db)
        for warehouse in city_data["warehouses"]:
            warehouse = await warehouse_service.create(WarehouseCreateSchemas(
                address=warehouse["address"],
                name=warehouse["name"],
                city=city.id
            ), db=db)
    await db.commit()


async def get_or_create(session, model, condition, **values):
    try:
        return (await session.execute(select(model).where(condition))).scalar_one()
    except NoResultFound:
        return (await session.execute(insert(model).values(**values).returning(model))).scalar_one()


async def create_groups_and_permissions() -> None:
    if settings.ENVIRONMENT == Environment.LOCAL:
        return
    print("Creating groups and permissions")
    session = async_session()
    for group, permissions in PERMISSIONS_MAP.items():
        group = await get_or_create(session, Group, Group.name == group.value, name=group.value, name_ru=GROUP_LOCALISATION[group]['ru'])
        for permission in permissions:
            await get_or_create(session, Permission, Permission.codename == permission, name=RUSSIAN_PERMISSIONS_MAP[permission], codename=permission)
            await get_or_create(session, auth_group_permission,
                                and_(auth_group_permission.c.codename == permission,
                                     auth_group_permission.c.group_id == group.id),
                                codename=permission, group_id=group.id)
    await session.commit()
