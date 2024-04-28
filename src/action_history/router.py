
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.action_history.service import action_history_service
from src.database import get_db
from src.users.auth import JWTBearer

router = APIRouter(tags=["Action History"])


@router.get("/order_items/{id}/action_history", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_200_OK)
async def get_action_history(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(JWTBearer()),
):
    return await action_history_service.get_order_action_history(id, user, db)
