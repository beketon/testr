from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.directions.models import TransportationType
from src.statistics.schemas import (OrdersStatistics, PaymentStatistics,
                                    TotalOrdersCount, TotalVolume,
                                    TotalWeightSchema, CourierStatisticsSchema)
from src.statistics.service import statistic_service
from src.users.auth import JWTBearer

router = APIRouter(
    tags=["Statistic"]
)


@router.get("/statistics/total_weight",
            dependencies=[Depends(JWTBearer()),
                          Depends(get_db)],
            response_model=TotalWeightSchema,
            status_code=status.HTTP_200_OK)
async def total_weight(db: AsyncSession = Depends(get_db), start_date: date = Query(None), end_date: date = Query(None),
                       direction_ids: List[int] = Query(None), transportation_type: TransportationType = Query(None)):
    return await statistic_service.total_weight(db=db, start_date=start_date, end_date=end_date, direction_ids=direction_ids, transportation_type=transportation_type)


@router.get("/statistics/total_volume",
            dependencies=[Depends(JWTBearer()),
                          Depends(get_db)],
            response_model=TotalVolume,
            status_code=status.HTTP_200_OK)
async def total_volume(db: AsyncSession = Depends(get_db), start_date: date = Query(None), end_date: date = Query(None),
                       direction_ids: List[int] = Query(None), transportation_type: TransportationType = Query(None)):
    return await statistic_service.total_volume(db=db, start_date=start_date, end_date=end_date, direction_ids=direction_ids, transportation_type=transportation_type)


@router.get("/statistics/total_orders_count",
            dependencies=[Depends(JWTBearer()),
                          Depends(get_db)],
            response_model=TotalOrdersCount,
            status_code=status.HTTP_200_OK)
async def total_orders_count(db: AsyncSession = Depends(get_db), start_date: date = Query(None),
                             end_date: date = Query(None), direction_ids: List[int] = Query(None), transportation_type: TransportationType = Query(None)):
    return await statistic_service.total_orders_count(db=db, start_date=start_date, end_date=end_date, direction_ids=direction_ids, transportation_type=transportation_type)


@router.get("/statistics/orders",
            dependencies=[Depends(JWTBearer()),
                          Depends(get_db)],
            response_model=List[OrdersStatistics],
            status_code=status.HTTP_200_OK)
async def orders(start_date: date = Query(None), end_date: date = Query(None), direction_ids: List[int] = Query(None),
                 db: AsyncSession = Depends(get_db), transportation_type: TransportationType = Query(None)):
    return await statistic_service.orders(start_date=start_date, end_date=end_date, direction_ids=direction_ids, db=db, transportation_type=transportation_type)


@router.get("/statistics/shippings",
            dependencies=[Depends(JWTBearer()),
                          Depends(get_db)],
            status_code=status.HTTP_200_OK)
async def shippings(start_date: date = Query(None), end_date: date = Query(None), direction_ids: List[int] = Query(None), db: AsyncSession = Depends(get_db)):
    return await statistic_service.shippings(start_date=start_date, end_date=end_date, direction_ids=direction_ids, db=db)


@router.get("/statistics/payments",
            dependencies=[Depends(JWTBearer()),
                          Depends(get_db)],
            response_model=List[PaymentStatistics],
            status_code=status.HTTP_200_OK)
async def payments(start_date: date = Query(None), end_date: date = Query(None), direction_ids: List[int] = Query(None), db: AsyncSession = Depends(get_db)):
    return await statistic_service.payments(start_date=start_date, end_date=end_date, direction_ids=direction_ids, db=db)


@router.get("/statistics/couriers",
            dependencies=[Depends(JWTBearer()),
                          Depends(get_db)],
            response_model=List[CourierStatisticsSchema],
            status_code=status.HTTP_200_OK)
async def get_courier_statistics(start_date: date = Query(None), end_date: date = Query(None),
                                 direction_ids: List[int] = Query(None),
                                 transportation_type: list[TransportationType] = Query(None),
                                 db: AsyncSession = Depends(get_db)) -> list[CourierStatisticsSchema]:
    return await statistic_service.get_courier_statistics(start_date=start_date, end_date=end_date,
                                                          direction_ids=direction_ids,
                                                          transportation_type=transportation_type, db=db)
