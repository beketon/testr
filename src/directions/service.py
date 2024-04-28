from typing import List

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy import delete, exc, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.dao.base import BaseDao
from src.database import get_db
from src.directions.models import Directions, TransportationType
from src.directions.schemas import (DirectionCreateSchemas,
                                    DirectionUpdateSchemas,
                                    DirectionViewSchemas)
from src.directions.utils import nested_serializer
from src.geography.models import City
from src.orders.models import Orders
from src.tarifs.models import CalculationType, Tarifs
from src.users.auth import get_password_hash
from src.users.models import Users
from src.users.perms import user_has_permissions
from src.users.schemas import Permission, UserViewSchemas
from src.users.service import GroupService, group_service


class DirectionService(BaseDao):
    class_name = Directions

    async def create_direction(self, payload: DirectionCreateSchemas, db: AsyncSession = Depends(get_db)):
        direction = await DirectionService.add({
            "arrival_city_id": payload.arrival_city_id,
            "departure_city_id": payload.departure_city_id,
            "is_active": payload.is_active,
            "transportation_type": payload.transportation_type,
            "email": payload.email,
            "password": payload.password
        })
        hashed_password = await get_password_hash(password=payload.password)
        user_model = Users
        user_set_model = user_model(
            email=payload.email,
            hashed_password=hashed_password,
            is_superuser=False,
            is_active=True,
            direction_id=direction.id,
            is_direction_user=True
        )
        price_for_air = (1000.0 / 6000.0) * 10000.0
        tarif = Tarifs(
            direction_id=direction.id,
            calculation_type=CalculationType.VOLUME,
            amount=1,
            price=price_for_air if payload.transportation_type != TransportationType.AIR else 15000.0
        )
        try:
            db.add(user_set_model)
            db.add(tarif)
            await db.commit()
        except exc.IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e._message))
        return await nested_serializer.serialize_by_id(direction.id, db)

    async def get_directions(self, transportation_type: list[TransportationType] = Query(None), search: str = None,
                             db: AsyncSession = Depends(get_db)) -> List[DirectionViewSchemas]:
        model = Directions
        query = select(model)
        if transportation_type:
            query = query.where(model.transportation_type.in_(
                [transportation_type.value for transportation_type in transportation_type]))
        if search:
            city_alias = aliased(City)
            query = query.join(City, model.arrival_city_id == City.id).join(city_alias,
                                                                            model.departure_city_id == city_alias.id).where(
                or_(
                    City.name.ilike(f"%{search}%"),
                    city_alias.name.ilike(f"%{search}%")
                )
            )
        execute_db = await db.execute(query)
        data = execute_db.scalars().all()
        resp = []
        for direction in data:
            resp.append(await nested_serializer.serialize_by_id(direction.id, db))
        return resp

    async def get_direction(self, id: int, db: AsyncSession = Depends(get_db)) -> DirectionViewSchemas:
        return await nested_serializer.serialize_by_id(id, db)

    async def delete_direction(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        direction = select(Directions).where(Directions.id == id)
        direction = await db.execute(direction)
        direction = direction.scalar_one_or_none()
        if direction:
            orders = await db.execute(select(Orders).where(Orders.direction_id == id))
            orders = orders.scalars().all()
            if orders:
                raise HTTPException(status_code=400, detail="Direction has orders")
            await db.execute(delete(Tarifs).where(Tarifs.direction_id == id))
            await db.delete(direction)
            await db.commit()
            return {"detail": "Direction deleted"}
        raise HTTPException(status_code=404, detail="Direction not found")

    async def update_direction(self, id: int, payload: DirectionUpdateSchemas, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        direction = select(Directions).where(Directions.id == id)
        direction = await db.execute(direction)
        direction = direction.scalar_one_or_none()
        if not direction:
            raise HTTPException(status_code=404, detail="Direction not found")
        if direction.is_active is not payload.is_active:
            await user_has_permissions(user.id, [Permission.UPDATE_DIRECTION_STATUS])
        try:
            hashed_password = await get_password_hash(password=payload.password)
            direction_user = await db.execute(select(Users).where(Users.direction_id == id))
            direction_user = direction_user.scalar_one_or_none()
            if direction_user:
                direction_user.email = payload.email
                direction_user.hashed_password = hashed_password
            stmt = (
                update(Directions)
                .where(Directions.id == id)
                .values(**payload.model_dump(exclude_unset=True))
            )
            await db.execute(stmt)
            await db.commit()
            await db.refresh(direction)
            return await nested_serializer.serialize_by_id(id, db)
        except exc.IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e._message))


direction_service = DirectionService()
