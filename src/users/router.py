from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.auth import JWTBearer
from src.users.models import Users
from src.users.schemas import (AuthGroupPermissionCreateSchemas,
                               AuthGroupPermissionViewSchemas,
                               ForgotPasswordEmail, GroupCreateSchemas,
                               GroupViewSchemas, GroupViewSchemasList,
                               PermissionViewSchemas, ResetForegetPassword,
                               ReviewsDriverCreateSchema,
                               ReviewsDriverListViewSchema,
                               ReviewsDriverViewSchema, Token,
                               UserConfirmationEmailSchemas, UserCreateSchemas,
                               UserPaginated, UserSchemas,
                               UserSetPasswordSchemas, UserUpdateSchemas,
                               UserViewSchemas)
from src.users.service import (group_permission, group_service,
                               permission_service, user_service)
from src.users.utils import func_user_has_permissions

router = APIRouter(
    tags=["User"]
)


@router.post("/login", status_code=status.HTTP_200_OK, response_model=Token)
async def login(payload: UserSchemas):
    return await user_service.login(payload)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await user_service.logout(user, db)


@router.get("/me",
            dependencies=[Depends(JWTBearer())],
            response_model=UserViewSchemas,
            status_code=status.HTTP_200_OK)
async def me(user: str = Depends(JWTBearer())):
    return await user_service.me(user)


@router.patch("/me",
              dependencies=[Depends(JWTBearer()),
                            Depends(get_db)],
              response_model=UserUpdateSchemas,
              status_code=status.HTTP_200_OK)
async def update_me(payload: UserUpdateSchemas, user: Users = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await user_service.update_me(payload, user, db)


@router.post("/superusers", status_code=status.HTTP_201_CREATED)
async def create_superuser(email: str, password: str):
    return await user_service.create_superuser(email, password)


@router.get("/users",
            dependencies=[Depends(JWTBearer())],
            status_code=status.HTTP_200_OK,
            response_model=UserPaginated)
async def get_users(group_id: int | None = None, district_id: int = Query(None), page: int = 1, limit: int = 10, user: str = Depends(JWTBearer()), search: str = Query(None)):
    return await user_service.get_users(group_id=group_id, page=page, limit=limit, user=user, search=search, district_id=district_id)


@router.get("/users/{id}",
            dependencies=[Depends(JWTBearer())],
            status_code=status.HTTP_200_OK,
            response_model=UserViewSchemas)
async def get_user(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await user_service.get_user(id, user, db)


@router.delete("/users/{id}",
               dependencies=[Depends(JWTBearer())],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await user_service.delete_user(id, user, db)


@router.patch("/users/{id}",
              dependencies=[Depends(JWTBearer())],
              status_code=status.HTTP_200_OK,
              response_model=UserUpdateSchemas)
async def update_user(id: int, payload: UserUpdateSchemas, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await user_service.update_user(id, payload, user, db)


@router.post("/users",
             dependencies=[Depends(JWTBearer())],
             status_code=status.HTTP_201_CREATED,
             response_model=UserViewSchemas)
async def create_user(payload: UserCreateSchemas, user: str = Depends(JWTBearer())):
    return await user_service.create_user(payload, user)


@router.post("/users/email-confirmation",
             status_code=status.HTTP_201_CREATED,
             response_model=Token)
async def confirm_email(payload: UserConfirmationEmailSchemas):
    return await user_service.confirm_email(payload)


@router.get("/groups", status_code=status.HTTP_200_OK,
            response_model=list[GroupViewSchemasList])
async def get_groups(db: AsyncSession = Depends(get_db)):
    return await group_service.all(db)


@router.post("/groups", status_code=status.HTTP_201_CREATED,
             response_model=GroupViewSchemas)
async def create_group(payload: GroupCreateSchemas, db: AsyncSession = Depends(get_db)):
    return await group_service.create(payload, db)


@router.patch("/groups/{id}", status_code=status.HTTP_200_OK,
              response_model=GroupViewSchemas)
async def update_group(id: int, payload: GroupCreateSchemas, db: AsyncSession = Depends(get_db)):
    return await group_service.update(id, payload, db)


@router.delete("/groups/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_group(id: int, db: AsyncSession = Depends(get_db)):
    return await group_service.delete(id, db)


@router.get("/permissions", status_code=status.HTTP_200_OK,
            response_model=list[PermissionViewSchemas])
async def get_permissions():
    return await permission_service.get()


@router.post("/group_permissions", status_code=status.HTTP_201_CREATED,
             response_model=AuthGroupPermissionViewSchemas)
async def create_group_permission(paylaod: AuthGroupPermissionCreateSchemas):
    return await group_permission.create(paylaod)


@router.get("/group_permissions", status_code=status.HTTP_200_OK,
            response_model=list[AuthGroupPermissionViewSchemas])
async def get_group_permissions():
    return await group_permission.get()


@router.post('/bulk_group_permissions', status_code=status.HTTP_204_NO_CONTENT)
async def create_bulk_group_permissions(payload: list[AuthGroupPermissionCreateSchemas], user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await group_permission.bulk_create(payload, db)


@router.get("/check")
async def check(user: Users = Depends(func_user_has_permissions(['string2']))):
    return {"detail": "OK"}


@router.post("/users/{user_id}/reviews",
             response_model=ReviewsDriverViewSchema,
             status_code=status.HTTP_201_CREATED)
async def create_review(user_id: int, payload: ReviewsDriverCreateSchema, user: Users = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await user_service.create_review(user_id=user_id, payload=payload, db=db, user=user)


@router.get("/users/{user_id}/reviews",
            response_model=ReviewsDriverListViewSchema,
            status_code=status.HTTP_200_OK)
async def get_review(user_id: int, db: AsyncSession = Depends(get_db)):
    return await user_service.get_review(user_id=user_id, db=db)


@router.post("/users/{user_id}/set_password", status_code=status.HTTP_200_OK)
async def set_password(user_id: int, payload: UserSetPasswordSchemas, user: Users = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await user_service.set_password(user_id, user, payload, db)


@router.post("/users/forgot_password", status_code=status.HTTP_200_OK, dependencies=[Depends(get_db)])
async def forgot_password(payload: ForgotPasswordEmail, db: AsyncSession = Depends(get_db)):
    return await user_service.forgot_password(payload=payload, db=db)


@router.post("/users/confirm_password", status_code=status.HTTP_200_OK, dependencies=[Depends(get_db)])
async def reset_password(payload: ResetForegetPassword, db: AsyncSession = Depends(get_db)):
    return await user_service.confirm_password(payload=payload, db=db)
