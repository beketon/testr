from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy import exc
from src.database import async_session
from src.exceptions import NotUnique


class BaseDao:
    class_name = None

    @classmethod
    async def find_by_id(cls, id: int):
        async with async_session() as session:
            query = select(cls.class_name).filter_by(id=id)
            data = await session.execute(query)
            resp = data.scalar_one_or_none()
            return resp

    @classmethod
    async def find_one_or_none(cls, filter):
        async with async_session() as session:
            query = select(cls.class_name).filter_by(**filter)
            data = await session.execute(query)
            resp = data.scalar_one_or_none()
            return resp

    @classmethod
    async def find_all(cls, filter):
        async with async_session() as session:
            query = select(cls.class_name).filter_by(**filter)
            data = await session.execute(query)
            resp = data.scalars().all()
            return resp

    @classmethod
    async def add(cls, data: Any):
        async with async_session() as session:
            data = cls.class_name(**data)
            try:
                session.add(data)
                await session.commit()
                await session.refresh(data)
                return data
            except exc.IntegrityError as e:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e._message))
        
    @classmethod
    async def all(cls):
        async with async_session() as session:
            query = select(cls.class_name)
            data = await session.execute(query)
            resp = data.scalars().all()
            return resp

    @classmethod
    async def delete(cls, filter):
        async with async_session() as session:
            query = select(cls.class_name).filter_by(**filter)
            data = await session.execute(query)
            resp = data.scalar_one_or_none()
            if not resp:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"{cls.class_name.__name__} not found")
            await session.delete(resp)
            await session.commit()

    @classmethod
    async def update(cls, id: int, data: Any):
        async with async_session() as session:
            stmt = (
                update(cls.class_name)
                .where(cls.class_name.id == id)
                .values(**data)
            )
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def add_all(cls, data: Any):
        async with async_session() as session:
            session.add_all(data)
            await session.commit()
            return data