from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDao
from src.database import get_db
from src.transportation_types.models import TransportationTypeDB
from src.transportation_types.schemas import TransportationTypeBase


class TransportationTypeService(BaseDao):
    class_name = TransportationTypeDB

    async def get_all(self, db: AsyncSession = Depends(get_db)):
        types = await TransportationTypeService.find_all({})
        return types

    async def get_by_id(self, id: int, db: AsyncSession = Depends(get_db)):
        type = await TransportationTypeService.find_by_id(id)
        return type

    async def create_transportation_type(self, transportation_type: TransportationTypeBase, db: AsyncSession = Depends(get_db)):
        type = await TransportationTypeService.add(transportation_type.dict())
        return type

    async def update_transportation_type(self, id: int, transportation_type: TransportationTypeBase, db: AsyncSession = Depends(get_db)):
        type = await TransportationTypeService.update(id, transportation_type.dict())
        return type

    async def delete_transportation_type(self, id: int, db: AsyncSession = Depends(get_db)):
        type = await TransportationTypeService.delete({"id": id})
        return type


transportation_type_service = TransportationTypeService()
