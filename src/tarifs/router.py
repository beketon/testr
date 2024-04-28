from fastapi import APIRouter, Depends, Query, status
from pydantic import conlist
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.tarifs.schemas import (CalculationType, TarifCreateSchemas,
                                TarifUpdateSchemas, TarifViewSchemas, TarifLimitSchemas, DeliveryTarifSchemas)
from src.tarifs.service import tarif_service
from src.users.auth import JWTBearer

router = APIRouter(
    tags=["Tarifs"]
)


@router.get("/tarifs", status_code=status.HTTP_200_OK, response_model=list[TarifViewSchemas])
async def get_tarifs(calculation_type: CalculationType, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db), direction_id: int = Query(None), ):
    return await tarif_service.get_tarifs(calculation_type=calculation_type, db=db, direction_id=direction_id)


@router.get("/delivery-tarifs", status_code=status.HTTP_200_OK, response_model=list[DeliveryTarifSchemas])
async def get_delivery_tarifs(calculation_type: CalculationType, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db), direction_id: int = Query(None)):
    return await tarif_service.get_delivery_tarifs(calculation_type=calculation_type, db=db, direction_id=direction_id)


@router.post("/tarifs", status_code=status.HTTP_204_NO_CONTENT)
async def create_range(payload: TarifCreateSchemas, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await tarif_service.create_tarifs(payload, db)


@router.post("/delivery-tarifs", status_code=status.HTTP_204_NO_CONTENT)
async def set_delivery_range(payload: list[DeliveryTarifSchemas], user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await tarif_service.set_delivery_tarifs(payload, db)


@router.get("/tarifs/limit", status_code=status.HTTP_200_OK, response_model=list[TarifLimitSchemas])
async def get_limit_range(direction_id: int, calculation_type: CalculationType, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await tarif_service.get_tarifs_limit(direction_id, calculation_type, db)


@router.post("/tarifs/limit", status_code=status.HTTP_204_NO_CONTENT)
async def create_update_limit_range(payload: TarifLimitSchemas, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await tarif_service.create_update_tarifs_limit(payload, db)


@router.patch("/tarifs", status_code=status.HTTP_204_NO_CONTENT)
async def update_range(payload: conlist(TarifUpdateSchemas, min_length=1), user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await tarif_service.update_tarifs(payload, db)
