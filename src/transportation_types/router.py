
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.transportation_types.schemas import TransportationTypeBase
from src.transportation_types.service import transportation_type_service
from src.users.auth import JWTBearer
from src.users.models import Users

router = APIRouter(tags=["Transportation Types"])


@router.post("/transportation_types", status_code=status.HTTP_201_CREATED)
async def create_transportation_type(transportation_type: TransportationTypeBase, db: AsyncSession = Depends(get_db), user: Users = Depends(JWTBearer())):
    return await transportation_type_service.create_transportation_type(transportation_type, db)


@router.get("/transportation_types")
async def get_transportation_types(db: AsyncSession = Depends(get_db)):
    return await transportation_type_service.get_all(db)


@router.get("/transportation_types/{id}")
async def get_transportation_type(id: int, db: AsyncSession = Depends(get_db)):
    return await transportation_type_service.get_by_id(id, db)


@router.put("/transportation_types/{id}")
async def update_transportation_type(id: int, transportation_type: TransportationTypeBase, db: AsyncSession = Depends(get_db), user: Users = Depends(JWTBearer())):
    return await transportation_type_service.update_transportation_type(id, transportation_type, db)


@router.delete("/transportation_types/{id}")
async def delete_transportation_type(id: int, db: AsyncSession = Depends(get_db), user: Users = Depends(JWTBearer())):
    return await transportation_type_service.delete_transportation_type(id, db)
