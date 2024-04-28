from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.expenses.schemas import (ExpenseCreateSchemas, ExpensePathSchemas,
                                  ExpenseViewSchemas)
from src.expenses.service import expense_service
from src.users.auth import JWTBearer
from src.users.models import Users
from src.users.perms import PermsRequired
from src.users.schemas import Permission

router = APIRouter(
    tags=["Expenses"]
)


@router.post("/expense", dependencies=[PermsRequired([Permission.CREATE_EXPENSE])], response_model=ExpenseViewSchemas)
async def create(payload: ExpenseCreateSchemas, user: Users = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await expense_service.create(payload=payload, user=user, db=db)


@router.get("/expense", dependencies=[PermsRequired([Permission.VIEW_EXPENSE])],
            response_model=List[ExpenseViewSchemas])
async def get(db: AsyncSession = Depends(get_db)):
    return await expense_service.get(db)


@router.get("/expense/{id}", dependencies=[PermsRequired([Permission.VIEW_EXPENSE])], response_model=ExpenseViewSchemas)
async def get_by_id(id: int, db: AsyncSession = Depends(get_db)):
    return await expense_service.get_by_id(id=id, db=db)


@router.patch("/expense/{id}",
              dependencies=[PermsRequired([Permission.UPDATE_EXPENSE])],
              response_model=ExpenseViewSchemas)
async def path(id: int, payload: ExpensePathSchemas, db: AsyncSession = Depends(get_db)):
    return await expense_service.path(id=id, payload=payload, db=db)


@router.delete("/expense/{id}",
               dependencies=[PermsRequired([Permission.DELETE_EXPENSE])],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    return await expense_service.delete(id=id, db=db)
