from datetime import date
from typing import Generic, TypeVar

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.directions.models import TransportationType
from src.directions.schemas import DirectionOut
from src.orders.schemas import OrderViewShortSchemas
from src.shipping.models import (Shipping, ShippingRespond,
                                 ShippingRespondStatus, ShippingWarehouse)
from src.shipping.schemas import ShippingViewSchema
from src.users.auth import JWTBearer
from src.users.models import Users
from src.warehouse.models import Warehouse
from src.warehouse.schemas import WarehouseOutShort

T = TypeVar("T")


class QueryFilter:
    @classmethod
    def filter_shippings(
            cls,
            class_name: Generic[T],
            data,
            status=None,
            status_ids=None,
            start_date: date = None,
            end_date: date = None,
            is_driver_contract_accepted: bool = None,
            transportation_type: TransportationType = None,
            direction_id: int = None,
            is_loaded: bool = None
    ):
        model = class_name
        if status is not None:
            data = data.where(model.respond_status == status.value)
        if start_date is not None:
            data = data.where(model.departure_date == start_date)
        if end_date is not None:
            data = data.where(model.arrival_date <= end_date)
        if status_ids is not None:
            data = data.where(model.status.in_(
                [status_group for status_group in status_ids]))
        if is_driver_contract_accepted is not None:
            data = data.where(
                model.is_driver_contract_accepted == is_driver_contract_accepted)
        if transportation_type is not None:
            data = data.where(model.shipping_type == transportation_type)
        if direction_id is not None:
            data = data.where(model.direction_id == direction_id)
        if is_loaded is not None:
            data = data.where(model.is_loaded == is_loaded)
        return data


async def enrich_shipping(shipping: Shipping, db: AsyncSession = Depends(get_db), user: Users = Depends(JWTBearer())):
    shipping_respond_model = ShippingRespond
    shipping_respond = select(shipping_respond_model).where(
        shipping_respond_model.shipping_id == shipping.id,
        shipping_respond_model.driver_id == user.id)
    shipping_respond_select = await db.execute(shipping_respond)
    shipping_respond_data = shipping_respond_select.scalar_one_or_none()
    if shipping_respond_data and shipping_respond_data.respond_status == ShippingRespondStatus.RESPONDED:
        is_responded = True
        is_accepted = False
        is_canceled = False
    elif shipping_respond_data and shipping_respond_data.respond_status in [ShippingRespondStatus.CONFIRMED, ShippingRespondStatus.FINISHED]:
        is_responded = True
        is_accepted = True
        is_canceled = False
    elif shipping_respond_data and shipping_respond_data.respond_status == ShippingRespondStatus.CANCEL:
        is_responded = False
        is_accepted = False
        is_canceled = True
    elif not shipping_respond_data:
        is_responded = False
        is_accepted = False
        is_canceled = False
    warehouse_shipping_query = select(ShippingWarehouse).options(selectinload(ShippingWarehouse.warehouse)).where(
        ShippingWarehouse.shipping_id == shipping.id
    )
    warehouse_shipping_select = await db.execute(warehouse_shipping_query)
    warehouse_shipping_data = warehouse_shipping_select.scalars().all()
    warehouse_shipping_out = [
        WarehouseOutShort(id=ws_data.warehouse.id, name=ws_data.warehouse.name, address=ws_data.warehouse.address)
        for ws_data in warehouse_shipping_data if ws_data.warehouse
    ]
    # TODO error of MissingGreenlet, temporary resolve of issue. original error: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)
    order_items_count = 0
    count_total_weight = 0
    orders_data = []
    for order in shipping.orders:
        order_items_count += len(order.order_items) if order.order_items else 0
        count_total_weight += order.total_weight
        order_dict = order.__dict__
        order_data = OrderViewShortSchemas(
            **order_dict
        )
        orders_data.append(order_data)
    shipping_dict = shipping.__dict__
    shipping_dict.pop('orders')
    serializer = ShippingViewSchema(
        **shipping_dict,
        orders=orders_data,
        warehouses=warehouse_shipping_out,
        is_responded=is_responded,
        is_accepted=is_accepted,
        is_canceled=is_canceled,
        order_items_count=order_items_count,
        count_total_weight=count_total_weight
        )
    return serializer
