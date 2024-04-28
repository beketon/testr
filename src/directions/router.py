from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.directions.models import TransportationType
from src.directions.schemas import (DirectionCreateSchemas,
                                    DirectionUpdateSchemas,
                                    DirectionViewSchemas)
from src.directions.service import direction_service
from src.users.auth import JWTBearer
from src.users.perms import PermsRequired
from src.users.schemas import Permission

router = APIRouter(
    tags=["Directions"]
)


@router.post("/directions", status_code=status.HTTP_201_CREATED, response_model=DirectionViewSchemas,
             dependencies=[PermsRequired([Permission.CREATE_DIRECTION])])
async def create_direction(payload: DirectionCreateSchemas, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await direction_service.create_direction(payload, db)


@router.get("/directions",
            response_model=list[DirectionViewSchemas],
            status_code=status.HTTP_200_OK)
async def get_directions(transportation_type: list[TransportationType] = Query(None), search: str = None, db: AsyncSession = Depends(get_db)):
    return await direction_service.get_directions(db=db, transportation_type=transportation_type, search=search)


@router.get("/directions/{id}",
            response_model=DirectionViewSchemas,
            status_code=status.HTTP_200_OK)
async def get_direction(id: int, db: AsyncSession = Depends(get_db)):
    return await direction_service.get_direction(id, db)


@router.patch("/directions/{id}",
              dependencies=[PermsRequired([Permission.UPDATE_DIRECTION])],
              status_code=status.HTTP_200_OK)
async def update_direction(id: int, payload: DirectionUpdateSchemas, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await direction_service.update_direction(id, payload, user, db)


@router.delete("/directions/{id}",
               dependencies=[PermsRequired([Permission.DELETE_DIRECTION])],
               status_code=status.HTTP_200_OK)
async def delete_direction(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await direction_service.delete_direction(id, user, db)
