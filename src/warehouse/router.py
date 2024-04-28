from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.auth import JWTBearer
from src.users.models import Users
from src.warehouse.schemas import (WarehouseCreateSchemas,
                                   WarehouseUpdateSchemas,
                                   WarehouseViewSchemas)
from src.warehouse.service import warehouse_service

router = APIRouter(
    tags=["Warehouse"]
)


@router.post("/warehouses", dependencies=[Depends(JWTBearer()), Depends(get_db)],
             status_code=status.HTTP_201_CREATED, response_model=WarehouseViewSchemas)
async def create_warehouse(payload: WarehouseCreateSchemas, db: AsyncSession = Depends(get_db)):
    return await warehouse_service.create(payload, db)


@router.get("/warehouses", status_code=status.HTTP_200_OK, response_model=list[WarehouseViewSchemas])
async def list_warehouses(db: AsyncSession = Depends(get_db), city_ids: list[int] = Query(None)):
    return await warehouse_service.get(db, city_ids=city_ids)


@router.get("/warehouses/{id}",
            dependencies=[Depends(JWTBearer()),
                          Depends(get_db)],
            status_code=status.HTTP_200_OK,
            response_model=WarehouseViewSchemas)
async def get_warehouse(id: int, db: AsyncSession = Depends(get_db)):
    return await warehouse_service.get_one(id, db)


@router.patch("/warehouses/{id}",
              dependencies=[Depends(JWTBearer()),
                            Depends(get_db)],
              status_code=status.HTTP_200_OK,
              response_model=WarehouseViewSchemas)
async def update_warehouse(id: int, payload: WarehouseUpdateSchemas, db: AsyncSession = Depends(get_db)):
    return await warehouse_service.update(id, payload, db)


@router.delete("/warehouses/{id}", dependencies=[Depends(JWTBearer()),
               Depends(get_db)], status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(id: int, db: AsyncSession = Depends(get_db)):
    return await warehouse_service.delete(id, db)
