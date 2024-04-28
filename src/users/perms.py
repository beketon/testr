from fastapi import Depends
from sqlalchemy import select

from src.database import get_db
from src.exceptions import PermissionDenied
from src.users.auth import JWTBearer
from src.users.models import Users
from src.users.service import permission_service


async def user_has_permissions(db, user_id: int, need_permissions: list[str]):
    permissions = {permission.codename for permission in await permission_service.get_permissions(user_id=user_id, db=db)}
    user = select(Users).where(Users.id == user_id)
    user = await db.execute(user)
    user = user.scalar_one()
    if user.is_superuser or user.is_direction_user:
        return
    if not set(need_permissions).issubset(set(permissions)):
        raise PermissionDenied


async def if_user_has_permissions(db, user_id: int, need_permissions: list[str]) -> bool:
    permissions = {permission.codename for permission in await permission_service.get_permissions(user_id=user_id, db=db)}
    user = select(Users).where(Users.id == user_id)
    user = await db.execute(user)
    user = user.scalar_one()
    if user.is_superuser or user.is_direction_user:
        return False
    if set(need_permissions).issubset(set(permissions)):
        return True
    return False


class PermsRequired:
    def __init__(self, perms: list[str]):
        self.perms = perms
        self.dependency = self
        self.use_cache = False

    async def __call__(self, user=Depends(JWTBearer()), db=Depends(get_db)):
        await user_has_permissions(db, user.id, self.perms)
