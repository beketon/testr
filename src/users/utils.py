from collections.abc import Callable
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy import select

from src.database import async_session
from src.users.auth import JWTBearer
from src.users.exceptions import RoleNotFound
from src.users.models import Users, auth_group_permission


def func_user_has_permissions(need_permissions: List[str] = None) -> Callable:
    """
    Dependency for generating authority authentication
    """

    async def user_has_permission(user: Users = Depends(JWTBearer())) -> Users:
        """
                 Is there a permission
        """
        if user.is_superuser:
            return user
        if not need_permissions:
            return user
        if user.group_id is None:
            raise RoleNotFound()
        async with async_session() as session:
            for need_permission in need_permissions:
                query = select(auth_group_permission).where(auth_group_permission.c.group_id == user.group_id).where(
                    auth_group_permission.c.codename == need_permission)
                data = await session.execute(query)
                resp = data.scalars().all()
                if not resp:
                    raise HTTPException(
                        status_code=403, detail="Permission denied")
            return user

    return user_has_permission

async def get_auth_group_permission(group_id: int):
    async with async_session() as session:
        query = select()