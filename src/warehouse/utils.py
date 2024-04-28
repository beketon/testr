from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session, get_db
from src.directions.models import Directions
from src.directions.schemas import DirectionOut
from src.exceptions import BadRequest
from src.geography.models import City, District
from src.geography.schemas import (CityOut, DistrictShortViewSchemas,
                                   GeographyViewSchemas)
from src.orders.models import OrderItems, Orders, Payment
from src.orders.schemas import OrderItemsOut, OrderViewSchemas, PaymentOut
from src.users.models import Users
from src.users.schemas import UserShortViewSchemas, UserViewSchemas
from src.warehouse.models import Warehouse
from src.warehouse.schemas import WarehouseViewSchemas


class WarehouseViewSerialized:

    async def serialize_by_id(self, id: int, db: AsyncSession = Depends(get_db)) -> WarehouseViewSchemas:
        warehouse_query = await db.execute(select(Warehouse).where(Warehouse.id == id))
        warehouse = warehouse_query.scalar_one_or_none()

        user_model = None
        user_query = await db.execute(select(Users).where(Users.id == warehouse.warehouse_user))
        user = user_query.scalar_one_or_none()
        if user:
            user_model = UserShortViewSchemas(**user.__dict__)

        city_query = await db.execute(select(City).where(City.id == warehouse.city))
        city = city_query.scalar_one_or_none()
        city_model = None
        if city:
            city_model = GeographyViewSchemas(**city.__dict__)

        district_query = await db.execute(select(District).where(District.id == warehouse.district))
        district = district_query.scalar_one_or_none()
        district_model = None
        if district:
            district_model = DistrictShortViewSchemas(
                id=district.id, name=district.name, city=city.id)
        order_items = await db.execute(select(OrderItems).where(OrderItems.warehouse_id == id))
        order_items = order_items.scalars().all()
        orders_items_number = len(order_items)
        orders = await db.execute(select(Orders).where(Orders.warehouse_id == id))
        orders = orders.scalars().all()
        orders_count = len(orders)
        warehouse_model = WarehouseViewSchemas(
            id=warehouse.id,
            address=warehouse.address,
            name=warehouse.name,
            city=city_model,
            warehouse_user=user_model,
            district=district_model,
            status=warehouse.status,
            orders_items_number=orders_items_number,
            phone=warehouse.phone,
            orders_count=orders_count
        )
        return warehouse_model


nested_serializer = WarehouseViewSerialized()
