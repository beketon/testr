from typing import List

from fastapi import Depends, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDao
from src.database import get_db
from src.users.models import Users
from src.warehouse.exceptions import WarehouseNotFound
from src.warehouse.models import Warehouse
from src.warehouse.schemas import (WarehouseCreateSchemas,
                                   WarehouseUpdateSchemas,
                                   WarehouseViewSchemas)
from src.warehouse.utils import nested_serializer


class WarehouseService(BaseDao):
    class_name = Warehouse

    async def create(self, payload: WarehouseCreateSchemas, db: AsyncSession = Depends(get_db)) -> WarehouseViewSchemas:
        warehouse = await WarehouseService.add({"address": payload.address, "name": payload.name, "city": payload.city,
                                                "warehouse_user": payload.warehouse_user, "district": payload.district,
                                                "status": payload.status, "phone": payload.phone})
        return await nested_serializer.serialize_by_id(warehouse.id, db)

    async def get(self, db: AsyncSession = Depends(get_db), city_ids: list[int] = Query(None)) -> List[WarehouseViewSchemas]:
        model = Warehouse
        query = select(model)
        if city_ids is not None:
            query = query.where(Warehouse.city.in_(city_ids))
        execute = await db.execute(query)
        data = execute.scalars().all()
        response = [await nested_serializer.serialize_by_id(warehouse.id, db) for warehouse in data]
        return response

    async def get_one(self, id: int, db: AsyncSession = Depends(get_db)) -> WarehouseViewSchemas:
        return await nested_serializer.serialize_by_id(id, db)

    async def update(self, id: int, payload: WarehouseUpdateSchemas, db: AsyncSession = Depends(get_db)) -> WarehouseViewSchemas:
        stmt = (
            update(Warehouse).
            where(Warehouse.id == id).
            values(**payload.model_dump(exclude_unset=True))
        )
        await db.execute(stmt)
        await db.commit()
        return await nested_serializer.serialize_by_id(id, db)

    async def delete(self, id: int, db: AsyncSession = Depends(get_db)):
        query = await db.execute(select(Warehouse).where(Warehouse.id == id))
        data = query.scalar_one_or_none()
        if data is None:
            raise WarehouseNotFound()
        await db.delete(data)
        await db.commit()


warehouse_service = WarehouseService()
