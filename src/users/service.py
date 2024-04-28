import asyncio
import random
import statistics

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy import delete, exc, func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.clients.sendgrid import mail_client
from src.common.models import SendEmail
from src.config import settings
from src.dao.base import BaseDao
from src.database import async_session, get_db
from src.exceptions import NotUnique
from src.geography.models import City, District
from src.geography.schemas import CityOut, DistrictShortViewSchemas
from src.users.auth import (JWTBearer, create_access_token, decodeJWT,
                            get_password_hash, verify_password)
from src.users.exceptions import (EmailNotFound, EmailTaken,
                                  InvalidCredentials, UserNotFound)
from src.users.models import (EmailCode, Group, OTPSigningCode, Permission,
                              ReviewsDriver, Users, auth_group_permission)
from src.users.schemas import (AuthGroupPermissionCreateSchemas,
                               ForgotPasswordEmail, GroupCreateSchemas,
                               GroupViewSchemas, ResetForegetPassword,
                               ReviewsDriverCreateSchema,
                               ReviewsDriverListViewSchema,
                               ReviewsDriverViewSchema, Token,
                               UserConfirmationEmailSchemas, UserCreateSchemas,
                               UserPaginated, UserSchemas,
                               UserSetPasswordSchemas, UserUpdateSchemas,
                               UserViewSchemas)


class EmailCodeService(BaseDao):
    class_name = EmailCode

    def code_generator(self):
        code = random.randint(1000, 9999)
        return code

    async def create_code(self, user_id: int, email: str):
        return await self.add({
            "email": email,
            "user_id": user_id,
            "code": str(self.code_generator())
        })


class GroupService(BaseDao):
    class_name = Group

    async def create(self, payload: GroupCreateSchemas, db: AsyncSession = Depends(get_db)) -> dict:
        async with db.begin():
            new_group = self.class_name(
                name=payload.name, name_ru=payload.name_ru)
            db.add(new_group)
            await db.flush()
            permissions = await db.execute(
                select(Permission).where(
                    Permission.codename.in_(payload.permissions))
            )
            permissions = permissions.scalars().all()
            for permission in permissions:
                association = auth_group_permission.insert().values(
                    group_id=new_group.id, codename=permission.codename)
                await db.execute(association)
            await db.commit()
            return {"id": new_group.id, "name": new_group.name, "name_ru": new_group.name_ru,
                    "permissions": [permission.codename for permission in permissions]}

    async def all(self, db: AsyncSession = Depends(get_db)) -> list[dict]:
        query = select(Group).options(selectinload(Group.permissions))
        result = await db.execute(query)
        groups = result.scalars().all()
        count_queries = [select(func.count(Users.id)).where(Users.group_id == group.id) for group in groups]
        count_results = await asyncio.gather(*[db.execute(q) for q in count_queries])
        for group, count_result in zip(groups, count_results):
            group.user_count = count_result.scalar()
        return [
            {
                "id": group.id,
                "name": group.name,
                "name_ru": group.name_ru,
                "user_count": group.user_count,
                "permissions": [{"codename": permission.codename, "name": permission.name} for permission in
                                group.permissions]
            }
            for group in groups
        ]

    async def update(self, group_id: int, payload: GroupCreateSchemas, db: AsyncSession = Depends(get_db)) -> dict:
        async with db.begin():
            group = await db.get(self.class_name, group_id)
            if not group:
                raise ValueError("Group not found")
            if payload.name:
                group.name = payload.name
            if payload.name_ru:
                group.name_ru = payload.name_ru
            await db.execute(delete(auth_group_permission).where(auth_group_permission.c.group_id == group_id))
            await db.flush()
            if payload.permissions:
                permissions = await db.execute(
                    select(Permission).where(Permission.codename.in_(payload.permissions)))
                permissions = permissions.scalars().all()
                for permission in permissions:
                    association = auth_group_permission.insert().values(group_id=group.id,
                                                                        codename=permission.codename)
                    await db.execute(association)
            await db.commit()
            return {"id": group.id, "name": group.name,
                    "permissions": [permission.codename for permission in permissions]}

    async def delete(self, group_id: int, db: AsyncSession = Depends(get_db)) -> dict:
        async with db.begin():
            group = await db.get(self.class_name, group_id)
            if not group:
                raise ValueError("Group not found")
            await db.execute(delete(auth_group_permission).where(auth_group_permission.c.group_id == group_id))
            await db.delete(group)
            await db.commit()
            return {"detail": "Group deleted"}


class PermissionService(BaseDao):
    class_name = Permission

    async def get(self) -> list[dict]:
        return await PermissionService.all()

    async def get_permissions(self, user_id: int, db: AsyncSession = Depends(get_db)) -> list[Permission]:
        return (await db.execute(
            select(Permission).join(
                auth_group_permission, Permission.codename == auth_group_permission.c.codename
            ).join(Users, Users.group_id == auth_group_permission.c.group_id).where(
                Users.id == user_id)
        )).scalars().all()


class AuthGroupPermissionService(BaseDao):
    class_name = auth_group_permission

    async def create(self, paylaod: AuthGroupPermissionCreateSchemas) -> dict:
        async with async_session() as session:
            try:
                query = auth_group_permission.insert().values(
                    group_id=paylaod.group_id, codename=paylaod.codename).returning(
                        auth_group_permission.c.id,
                        auth_group_permission.c.group_id,
                        auth_group_permission.c.codename
                )
                data = await session.execute(query)
                inserted_data = data.first()
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise NotUnique()
            return inserted_data

    async def bulk_create(self, payload: list[AuthGroupPermissionCreateSchemas], db: AsyncSession = Depends(get_db)):
        try:
            group_permissions = [{'group_id': group_permission.group_id,
                                  'codename': group_permission.codename} for group_permission in payload]
            await db.execute(auth_group_permission.insert(), group_permissions)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise NotUnique()

        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    async def get(self) -> list[dict]:
        async with async_session() as session:
            query = select(auth_group_permission)
            result = await session.execute(query)
            return result


class UserService(BaseDao):
    class_name = Users

    def password_generator(self) -> str:
        chars = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        password = ''.join(random.choice(chars) for i in range(8))
        return password

    async def create_user(self, payload: UserCreateSchemas, creator: UserViewSchemas):
        user = await UserService.find_one_or_none({"email": payload.email})
        if user:
            raise EmailTaken()
        password = self.password_generator()
        hashed_password = await get_password_hash(password=password)
        session = async_session()
        group = await session.execute(select(Group).where(Group.id == payload.group_id))
        city = await session.execute(select(City).where(City.id == payload.city_id))
        district = await session.execute(select(District).where(District.id == payload.district_id))
        group = group.scalars().first()
        city = city.scalars().first()
        district = district.scalars().first()
        user = Users(
            email=payload.email,
            hashed_password=hashed_password,
            city=city.id,
            group_id=group.id,
            district_id=district.id if district else None,
            creator=creator.id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            middle_name=payload.middle_name,
            phone=payload.phone,
            longitude=payload.longitude,
            latitude=payload.latitude,
            car_mark=payload.car_mark,
            car_plate_number=payload.car_plate_number,
            car_engine_volume=payload.car_engine_volume,
            direction_id=payload.direction_id,
            warehouse_id=payload.warehouse_id
        )
        url = f"{settings.FRONTEND_URL}"
        send_mail = SendEmail(
            email=payload.email,
            subject="Войдите в аккаунт B-Express",
            message=f"Ваш пароль: {password} \n Ссылка для входа: {url}"
        )
        mail_client.send(send_mail)
        session.add(user)
        await session.commit()
        user_dict = user.__dict__
        user_dict['city'] = CityOut(id=city.id, name=city.name)
        user_view = UserViewSchemas(
            **user_dict,
            password=password
        )
        return user_view

    async def logout(self, user: Users, db: AsyncSession = Depends(get_db)):
        user.device_registration_id = None
        await db.commit()
        return {"detail": "User has been logged out"}

    def validate_password(self, password: str, confirm_password: str):
        if password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")
        if not any(char.isupper() for char in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one uppercase letter")
        if not any(char.islower() for char in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one lowercase letter")

    async def set_password(self, user_id: int, user: Users, payload: UserSetPasswordSchemas, db: AsyncSession = Depends(get_db)):
        self.validate_password(payload.password, payload.confirm_password)
        employee = await UserService.find_one_or_none({"id": user_id})
        if not employee:
            raise UserNotFound()
        hashed_password = await get_password_hash(password=payload.password)
        stmt = (update(Users) .where(Users.id == user_id) .values(
            hashed_password=hashed_password))
        await db.execute(stmt)
        await db.commit()
        return {"detail": "Password has been updated"}

    async def me(self, user: UserViewSchemas) -> UserViewSchemas:
        user = select(Users).where(Users.id == user.id)
        session = async_session()
        result = await session.execute(user)
        user = result.scalars().first()
        city = await session.execute(select(City).where(City.id == user.city))
        city = city.scalars().first()
        district = await session.execute(select(District).where(District.id == user.district_id))
        district = district.scalars().first()
        user_dict = user.__dict__
        if user.city:
            user_dict['city'] = CityOut(id=city.id, name=city.name)
        group = await session.execute(
            select(Group).options(selectinload(Group.permissions)).where(
                Group.id == user.group_id)
        )
        group = group.scalars().first()
        permissions = [
            perm.codename for perm in group.permissions] if group else []
        user_dict.pop('group_id')
        user_dict.pop('group')
        return UserViewSchemas(
            **user_dict,
            district=None if not district else DistrictShortViewSchemas(
                id=district.id, name=district.name, city=district.city_id),
            group=GroupViewSchemas(
                id=group.id, name=group.name, permissions=permissions) if group else None
        )

    async def update_me(self, payload: UserUpdateSchemas, user: Users = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
        model = Users
        query = await db.execute(select(model).where(model.id == user.id))
        data = query.scalar_one_or_none()
        if not data:
            raise EmailNotFound()
        try:
            city = await db.execute(select(City).where(City.id == payload.city_id))
            if not city:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
            stmt = (update(Users) .where(Users.id == user.id) .values(
                **payload.model_dump(exclude_unset=True, exclude={"city_id"}), city=payload.city_id))
            await db.execute(stmt)
            await db.commit()
            await db.refresh(data)
            return payload
        except exc.IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e._message))

    async def delete_user(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        model = Users
        query = await db.execute(select(model).where(model.id == id))
        data = query.scalar_one_or_none()
        if not data:
            raise EmailNotFound()
        await db.delete(data)
        await db.commit()
        return data

    async def update_user(self, id: int, payload: UserUpdateSchemas, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        model = Users
        query = await db.execute(select(model).where(model.id == id))
        data = query.scalar_one_or_none()
        if not data:
            raise EmailNotFound()
        city = await db.execute(select(City).where(City.id == payload.city_id))
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
        try:
            stmt = (
                update(Users)
                .where(Users.id == id)
                .values(
                    **payload.model_dump(exclude_unset=True, exclude={"city_id"}),
                    city=payload.city_id
                )
            )
            await db.execute(stmt)
            await db.commit()
            await db.refresh(data)
            return payload
        except exc.IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e._message))

    async def enrich_user(self, user: Users, db: AsyncSession = Depends(get_db)) -> UserViewSchemas:
        city = await db.execute(select(City).where(City.id == user.city))
        city = city.scalars().first()
        district = await db.execute(select(District).where(District.id == user.district_id))
        district = district.scalars().first()
        user_dict = user.__dict__
        if user.city:
            user_dict['city'] = CityOut(id=city.id, name=city.name)
        group = await db.execute(
            select(Group).options(selectinload(Group.permissions)).where(
                Group.id == user.group_id)
        )
        group = group.scalars().first()
        permissions = [
            perm.codename for perm in group.permissions] if group else []
        user_dict.pop('group_id')
        user_dict.pop('group')
        user_view = UserViewSchemas(
            **user_dict,
            district=DistrictShortViewSchemas(
                id=district.id,
                name=district.name,
                city=district.city_id) if district else None,
            group=GroupViewSchemas(
                id=group.id,
                name=group.name,
                permissions=permissions) if group else None
        )
        return user_view

    async def get_user(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)) -> UserViewSchemas:
        model = Users
        query = await db.execute(select(model).where(model.id == id))
        data = query.scalar_one_or_none()
        if not data:
            raise EmailNotFound()
        return await self.enrich_user(data, db)

    def search(self, users, search: str = None):
        if search and not search.isspace():
            users = users.join(City).where(or_(Users.first_name.ilike(f"%{search}%"), Users.last_name.ilike(
                f"%{search}%"), Users.middle_name.ilike(f"%{search}%"), Users.phone.ilike(f"%{search}%"),
                Users.email.ilike(f"%{search}%"), City.name.ilike(f"%{search}%")))
        return users

    async def get_users(self, district_id: int = Query(None), group_id: int | None = None, page: int = 1, limit: int = 10, user: UserViewSchemas = None, search: str = None) -> UserPaginated:
        session = async_session()
        filtered_users = select(Users)
        if group_id:
            filtered_users = filtered_users.where(Users.group_id == group_id)
        if district_id:
            filtered_users = filtered_users.where(
                Users.district_id == district_id)
        filtered_users = self.search(filtered_users, search)
        result = await session.execute(self.paginate(filtered_users, page, limit))
        users = result.scalars().all()
        users_view = [await self.enrich_user(user, session) for user in users]
        total = await session.execute(filtered_users)
        total = len(total.scalars().all())
        pages_number = total // limit
        if total % limit != 0:
            pages_number += 1
        return UserPaginated(
            total=total,
            pages_number=pages_number,
            data=users_view,
            page=page,
            limit=limit)

    def paginate(self, users, page: int, limit: int):
        return users.offset((page - 1) * limit).limit(limit)

    async def login(self, payload: UserSchemas) -> dict:
        session = async_session()
        user = await UserService.find_one_or_none({"email": payload.email})
        if not user:
            raise EmailNotFound()
        if not await verify_password(plain_password=payload.password, hashed_password=user.hashed_password):
            raise InvalidCredentials()
        access_token = await create_access_token({"user_id": str(user.id)})
        if payload.device_registration_id:
            user.device_registration_id = payload.device_registration_id
            await session.execute(update(Users).where(Users.id == user.id).values(device_registration_id=payload.device_registration_id))
            await session.commit()
        return Token(access_token=access_token, token_type="bearer")

    async def create_superuser(self, email: str, password: str):
        hashed_password = await get_password_hash(password=password)
        user = await UserService.find_one_or_none({"email": email})
        if user:
            print("Email already exists")
            raise EmailTaken()
        user = Users(
            email=email,
            hashed_password=hashed_password,
            is_superuser=True,
            first_name="SUPER",
            last_name="SUPER",
            city=1,
            is_active=True
        )
        session = async_session()
        session.add(user)
        await session.commit()
        return user

    async def confirm_email(self, payload: UserConfirmationEmailSchemas) -> Token:
        code: EmailCode = await email_service.find_one_or_none({"code": payload.code, "user_id": payload.user_id})
        if not code:
            raise EmailNotFound()
        user: Users = await UserService.find_one_or_none({"id": payload.user_id})
        if not user:
            raise EmailNotFound()
        user.is_active = True
        hashed_password = await get_password_hash(password=payload.password)
        user.hashed_password = hashed_password
        access_token = await create_access_token({"user_id": str(user.id)})
        await UserService.update(id=user.id, data=user.to_dict())
        return Token(access_token=access_token, token_type="bearer")

    async def create_review(self, user_id: int, payload: ReviewsDriverCreateSchema, user: Users = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)) -> ReviewsDriverViewSchema:
        model = ReviewsDriver
        set_model = model(**payload.model_dump(),
                          driver_id=user_id, creator_id=user.id)
        try:
            db.add(set_model)
            await db.commit()
            await db.refresh(set_model)
        except exc.IntegrityError:
            await db.rollback()
            raise UserNotFound()
        user_model = Users
        user_query = await db.execute(select(user_model).where(user_model.id == user_id))
        user_data = user_query.scalar_one_or_none()
        if user_data:
            review_query = await db.execute(select(model))
            review_data = review_query.scalars().all()
            stars = [item.star for item in review_data]
            if len(stars) > 0:
                user_data.rating = statistics.mean(stars)
                await db.commit()
        return set_model

    async def get_review(self, user_id: int, db: AsyncSession = Depends(get_db)) -> ReviewsDriverListViewSchema:
        model = ReviewsDriver
        query = await db.execute(select(model).where(model.driver_id == user_id))
        data = query.scalars().all()
        result = [ReviewsDriverViewSchema(**item.__dict__) for item in data]
        number_of_reviews = await db.scalar(select(func.count(model.id)).select_from(model).where(model.driver_id == user_id))
        reviews = ReviewsDriverListViewSchema(
            data=result, number_of_reviews=number_of_reviews)
        return reviews

    async def forgot_password(self, payload: ForgotPasswordEmail, db: AsyncSession = Depends(get_db)) -> dict:
        user = await db.execute(select(Users).where(Users.email == payload.email))
        user_data = user.scalars().first()
        if not user_data:
            raise EmailNotFound()
        email_code = await EmailCodeService().create_code(user_id=user_data.id, email=payload.email)
        forget_url_link = f"{payload.base_url}?token={email_code.code}"
        if payload.is_mobile_device:
            message = f"Код для восстановления пароля: {email_code.code}"
        else:
            message = f"Ссылка для восстановления пароля: {forget_url_link}"
        send_mail = SendEmail(
            email=payload.email,
            subject="Восстановление пароля",
            message=message
        )
        mail_client.send(send_mail)
        return {"detail": "Ссылка для восстановления пароля отправлена на вашу почту",
                "link": forget_url_link, "code": email_code.code, "user_id": user_data.id}

    async def confirm_password(self, payload: ResetForegetPassword, db: AsyncSession = Depends(get_db)) -> dict:
        email_code = await db.execute(select(EmailCode).where(EmailCode.code == payload.secret_token))
        email_code = email_code.scalars().first()
        if not email_code:
            raise EmailNotFound()
        user = await db.execute(select(Users).where(Users.id == email_code.user_id))
        if not user:
            raise UserNotFound()
        user = user.scalars().first()
        if payload.new_password != payload.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Пароли не совпадают")
        hashed_password = await get_password_hash(password=payload.new_password)
        user.hashed_password = hashed_password
        await db.delete(email_code)
        await db.commit()
        return {"detail": "Пароль успешно изменен"}


user_service = UserService()
group_service = GroupService()
permission_service = PermissionService()
email_service = EmailCodeService()
group_permission = AuthGroupPermissionService()
