from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.action_history.models import (ACTION_CODE_TO_ACTION_DESCRIPTION,
                                       ActionCode, ActionHistory)
from src.action_history.schemas import (ActionHistoryCreate,
                                        ActionHistoryShortOut)
from src.database import get_db
from src.geography.models import City
from src.users.models import Users
from src.users.schemas import UserViewSchemas
from src.warehouse.models import Warehouse


class ActionHistoryService:
    async def get_action_code_description(self, action: ActionHistoryCreate, db: AsyncSession = Depends(get_db)) -> str:
        if (action.action_code == ActionCode.MANAGER_APPROVED):
            manager = await db.execute(select(Users).where(Users.id == action.manager_id))
            manager = manager.scalar_one_or_none()
            action_description = ACTION_CODE_TO_ACTION_DESCRIPTION[
                action.action_code] % manager.full_name
        elif (action.action_code in [ActionCode.COURIER_DELIVERING_TO_WAREHOUSE, ActionCode.DELIVERING_TO_RECIPIENT]):
            courier = await db.execute(select(Users).where(Users.id == action.courier_id))
            courier = courier.scalar_one_or_none()
            action_description = ACTION_CODE_TO_ACTION_DESCRIPTION[
                action.action_code] % courier.fl_name
        elif (action.action_code in [ActionCode.ACCEPTED_TO_WAREHOUSE, ActionCode.ARRIVED_TO_DESTINATION]):
            warehouse = await db.execute(select(Warehouse).where(Warehouse.id == action.warehouse_id))
            warehouse = warehouse.scalar_one_or_none()
            city = await db.execute(select(City).where(City.id == warehouse.city))
            city = city.scalar_one_or_none()
            manager = await db.execute(select(Users).where(Users.id == action.warehouse_manager_id))
            manager = manager.scalar_one_or_none()
            action_description = ACTION_CODE_TO_ACTION_DESCRIPTION[action.action_code] % (
                warehouse.name, city.name, manager.fl_name)
        elif (action.action_code == ActionCode.DELIVERED):
            courier = await db.execute(select(Users).where(Users.id == action.courier_id))
            courier = courier.scalar_one_or_none()
            if courier:
                action_description = ACTION_CODE_TO_ACTION_DESCRIPTION[
                    action.action_code] % courier.fl_name
            else:
                action_description = ACTION_CODE_TO_ACTION_DESCRIPTION[
                    action.action_code] % "Самовывоз"
        else:
            action_description = ACTION_CODE_TO_ACTION_DESCRIPTION[action.action_code]
        return action_description

    async def add_action(self, action: ActionHistoryCreate, db: AsyncSession = Depends(get_db)):
        if action.order_item_id:
            action_history_db = (await db.execute(select(ActionHistory).where(ActionHistory.order_item_id == action.order_item_id).where(
                ActionHistory.action_code == action.action_code.value))).scalars()
            action_history_db = action_history_db.first()
        elif action.order_id:
            action_history_db = (await db.execute(select(ActionHistory).where(ActionHistory.order_id == action.order_id).where(
                ActionHistory.action_code == action.action_code.value))).scalars()
            action_history_db = action_history_db.first()
        action_description = await self.get_action_code_description(action, db)
        action_history = ActionHistory(
            **action.dict(exclude={"action_code"}),
            action_code=action.action_code.value,
            action_description=action_description
        )
        if not action_history_db:
            db.add(action_history)
            await db.commit()
            await db.refresh(action_history)
        return action_history

    async def get_order_action_history(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)) -> list[ActionHistoryShortOut]:
        action_history = await db.execute(select(ActionHistory).where(ActionHistory.order_item_id == id).order_by(ActionHistory.created_at))
        action_history = action_history.scalars().all()
        return [ActionHistoryShortOut(**action_history_item.__dict__) for action_history_item in action_history]


action_history_service = ActionHistoryService()
