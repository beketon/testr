from typing import List

from fastapi import Depends
from sqlalchemy import exc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.exceptions import IdNotFound
from src.expenses.exceptions import ExpenseNotFound, ExpenseNotUnique
from src.expenses.models import Expense
from src.expenses.schemas import (ExpenseCreateSchemas, ExpensePathSchemas,
                                  ExpenseViewSchemas)
from src.users.auth import JWTBearer
from src.users.models import Users
from sqlalchemy.orm import joinedload


class ExpenseService:
    async def create(self, payload: ExpenseCreateSchemas, user: Users = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)) -> ExpenseViewSchemas:
        try:
            model = Expense
            set_model = model(creator=user.id, **payload.model_dump())
            db.add(set_model)
            await db.commit()
            await db.refresh(set_model)
            return set_model
        except exc.IntegrityError:
            await db.rollback()
            raise ExpenseNotUnique()

    async def get(self, db: AsyncSession = Depends(get_db)) -> List[ExpenseViewSchemas]:
        model = Expense
        query = await db.execute(select(model))
        data = query.scalars().all()
        return data
        
    async def get_by_id(self, id: int = None, db: AsyncSession = Depends(get_db)) -> ExpenseViewSchemas:
        if not id:
            raise IdNotFound()
        model = Expense
        query = await db.execute(select(model).where(model.id == id))
        data = query.scalar_one_or_none()
        if not data:
            raise ExpenseNotFound()
        return data

    async def path(self, id: int, payload: ExpensePathSchemas, db: AsyncSession = Depends(get_db)) -> ExpenseViewSchemas:
        if not id:
            raise IdNotFound()
        model = Expense
        query = await db.execute(select(model).where(model.id == id))
        data = query.scalar_one_or_none()
        if not data:
            raise ExpenseNotFound()
        stmt = (
                update(Expense)
                .where(Expense.id == id)
                .values(**payload.model_dump(exclude_unset=True))
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(data)
        return data

    async def delete(self, id: int, db: AsyncSession = Depends(get_db)) -> None:
        if not id:
            raise IdNotFound()
        model = Expense
        query = await db.execute(select(model).where(model.id == id))
        data = query.scalar_one_or_none()
        if not data:
            raise ExpenseNotFound()
        await db.delete(data)
        await db.commit()

expense_service = ExpenseService()