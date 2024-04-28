import asyncio
import io
import math
import os
import random
import subprocess
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

from docx import Document
from fastapi import Depends, File, HTTPException, UploadFile, status
from sqlalchemy import (String, and_, asc, cast, delete, desc, func, not_, or_,
                        select, update)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, selectinload
from starlette.responses import StreamingResponse

from src.action_history.models import ActionCode
from src.action_history.schemas import (ActionHistoryCreate,
                                        SetOrderItemWarehouseStatus)
from src.action_history.service import action_history_service
from src.clients.whatsapp import whatsapp_client
from src.common.models import SortOrder
from src.common.service import file_service
from src.config import settings
from src.constants import Environment
from src.dao.base import BaseDao
from src.database import get_db
from src.directions.models import Directions, TransportationType
from src.exceptions import PermissionDenied
from src.expenses.models import Expense, order_expenses
from src.geography.models import City
from src.notification.models import (NOTIFICATION_TEMPLATES, NotificationCode,
                                     SmsCode)
from src.notification.service import notification_service
from src.orders.models import (DeliveryType, OrderItems, OrderPhoto, Orders,
                               OrderStatus, Payment, PaymentStatus)
from src.orders.schemas import (CancelledOrder, CourierDeliverySchema,
                                Currency, ExpensesTotalPrice,
                                NotDeliveredOrder, OrderItemsCreateSchemas,
                                OrderItemsPaginated, OrderItemsViewSchemas,
                                OrderPaginated, OrdersCreateSchemas,
                                OrderUpdateSchemas, OrderViewSchemas,
                                PayerType, PaymentUpdateSchemas,
                                SendOTPSigning, SignOrderOTP, TotalAmount,
                                TotalAmountOrder)
from src.orders.utils import nested_serializer
from src.shipping.models import (Shipping, ShippingRespond,
                                 ShippingRespondStatus, ShippingStatus,
                                 ShippingWarehouse)
from src.tarifs.models import CalculationType, Tarifs
from src.users.models import Group, OTPSigningCode, OTPType, Users, UsersOrders
from src.users.perms import if_user_has_permissions
from src.users.schemas import GroupEnum, Permission, UserViewSchemas
from src.warehouse.models import Warehouse


class OrderItemService:
    async def add(self, payload: OrderItemsCreateSchemas, user: UserViewSchemas, file: UploadFile = File(None), db: AsyncSession = Depends(get_db)) -> OrderItemsViewSchemas:
        file_s3 = await file_service.upload_file(file.filename, file.file)
        order_item = select(OrderItems).where(
            OrderItems.qr_code_hash == payload.qr_code_hash)
        order_item = await db.execute(order_item)
        order_item = order_item.scalar_one_or_none()
        if order_item is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Order item with this qr code already exists")
        order = select(Orders).where(Orders.id == payload.order_id)
        order = await db.execute(order)
        order = order.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        order_item = OrderItems(
            **payload.model_dump(),
            status=order.order_status,
            photo=file_s3["file_path"])
        db.add(order_item)
        await db.commit()
        await db.refresh(order_item)
        if (order.order_status == OrderStatus.ACCEPTED_TO_WAREHOUSE.value):
            action_code = ActionCode.ACCEPTED_TO_WAREHOUSE
            await action_history_service.add_action(ActionHistoryCreate(order_item_id=order_item.id, warehouse_manager_id=user.id, warehouse_id=order.start_warehouse_id, action_code=action_code), db)
        elif (order.order_status == OrderStatus.COURIER_DELIVERING_TO_WAREHOUSE.value):
            action_code = ActionCode.COURIER_DELIVERING_TO_WAREHOUSE
            await action_history_service.add_action(ActionHistoryCreate(order_item_id=order_item.id, courier_id=user.id, action_code=action_code), db)
        elif (order.order_status in [OrderStatus.CREATED.value, OrderStatus.ASSIGNED_TO_COURIER.value, OrderStatus.CLIENT_DELIVERING_TO_WAREHOUSE.value]):
            action_code = ActionCode.CREATED
            await action_history_service.add_action(ActionHistoryCreate(order_item_id=order_item.id, action_code=action_code), db)
        return order_item

    async def delete(self, id: int, db: AsyncSession = Depends(get_db)) -> None:
        query = await db.execute(select(OrderItems).where(OrderItems.id == id))
        data = query.scalar_one_or_none()
        if data is None:
            raise HTTPException(status_code=404, detail="Order item not found")
        if data.photo:
            await file_service.delete_file(data.photo)
        await db.delete(data)
        await db.commit()

    async def get(self, id: int, db: AsyncSession = Depends(get_db)) -> OrderItemsViewSchemas:
        query = await db.execute(select(OrderItems).where(OrderItems.id == id))
        data = query.scalar_one_or_none()
        if data is None:
            raise HTTPException(status_code=404, detail="Order item not found")
        return data

    async def set_as_courier_delivering_to_warehouse(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        order_item = await db.execute(select(OrderItems).where(OrderItems.id == id))
        order_item = order_item.scalar_one_or_none()
        if order_item is None:
            raise HTTPException(status_code=404, detail="Order item not found")
        await db.execute(update(OrderItems).where(OrderItems.id == id).values(status=OrderStatus.COURIER_DELIVERING_TO_WAREHOUSE.value))
        await db.commit()
        await action_history_service.add_action(ActionHistoryCreate(order_item_id=id, courier_id=user.id, action_code=ActionCode.COURIER_DELIVERING_TO_WAREHOUSE), db)
        return order_item

    async def set_as_accepted_to_warehouse(self, status: SetOrderItemWarehouseStatus, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        order_item = await db.execute(select(OrderItems).where(OrderItems.id == status.order_item_id))
        order_item = order_item.scalar_one_or_none()
        if order_item is None:
            raise HTTPException(status_code=404, detail="Order item not found")
        order_item_status = order_item.status
        await db.execute(update(OrderItems).where(OrderItems.id == order_item.id).values(status=OrderStatus.ACCEPTED_TO_WAREHOUSE.value, warehouse_id=status.warehouse_id))
        await db.commit()
        warehouse = select(Warehouse).where(
            Warehouse.id == status.warehouse_id)
        warehouse = await db.execute(warehouse)
        warehouse = warehouse.scalar_one_or_none()
        if warehouse is None:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        if order_item_status == OrderStatus.ACCEPTED_TO_WAREHOUSE.value:
            await action_history_service.add_action(
                ActionHistoryCreate(order_item_id=order_item.id, warehouse_manager_id=user.id,
                                    warehouse_id=warehouse.id, action_code=ActionCode.ARRIVED_MIDDLE_WAREHOUSE), db)
        else:
            await action_history_service.add_action(ActionHistoryCreate(order_item_id=order_item.id, warehouse_manager_id=user.id, warehouse_id=warehouse.id, action_code=ActionCode.ACCEPTED_TO_WAREHOUSE), db)
        order = await db.execute(select(Orders).where(Orders.id == order_item.order_id))
        order = order.scalar_one_or_none()
        if order and order.order_status == OrderStatus.COURIER_DELIVERING_TO_WAREHOUSE.value and order.courier:
            new_association = UsersOrders(
                user_id=order.courier,
                order_id=order.id,
                status=OrderStatus.ACCEPTED_TO_WAREHOUSE.value
            )
            db.add(new_association)
        order_status = order.order_status if order else None
        is_all_items_accepted = True
        for item in order.order_items:
            if item.status != OrderStatus.ACCEPTED_TO_WAREHOUSE.value:
                is_all_items_accepted = False
                break
        if is_all_items_accepted:
            await db.execute(update(Orders).where(Orders.id == order.id).values(order_status=OrderStatus.ACCEPTED_TO_WAREHOUSE.value, warehouse_id=warehouse.id, start_warehouse_id=warehouse.id))
            if order_status == OrderStatus.ACCEPTED_TO_WAREHOUSE.value:
                await action_history_service.add_action(
                    ActionHistoryCreate(order_id=order.id, warehouse_manager_id=user.id, warehouse_id=warehouse.id,
                                        action_code=ActionCode.ARRIVED_MIDDLE_WAREHOUSE), db)
            else:
                await action_history_service.add_action(ActionHistoryCreate(order_id=order.id, warehouse_manager_id=user.id, warehouse_id=warehouse.id, action_code=ActionCode.ACCEPTED_TO_WAREHOUSE), db)
            if order.courier:
                await db.execute(update(Users).where(Users.id == order.courier).values(selected_orders=Users.selected_orders + 1))
        await db.commit()
        return order_item

    # TODO: refactor this function
    async def set_as_arrived_to_destination(self, status: SetOrderItemWarehouseStatus, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        order_item = await db.execute(select(OrderItems).where(OrderItems.id == status.order_item_id))
        order_item = order_item.scalar_one_or_none()
        if order_item is None:
            raise HTTPException(status_code=404, detail="Order item not found")
        warehouse = select(Warehouse).where(
            Warehouse.id == status.warehouse_id)
        warehouse = await db.execute(warehouse)
        warehouse = warehouse.scalar_one_or_none()
        if warehouse is None:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        order = await db.execute(select(Orders).where(Orders.id == order_item.order_id))
        order = order.scalar_one_or_none()
        shipping_ids = [shipping.id for shipping in order.shippings]
        if shipping_ids:
            update_query = update(ShippingWarehouse).where(
                and_(
                    ShippingWarehouse.shipping_id.in_(shipping_ids),
                    ShippingWarehouse.warehouse_id == status.warehouse_id
                )
            ).values(is_visited=True)
            await db.execute(update_query)
            await db.commit()
        for shipping in order.shippings:
            sw_query = await db.execute(
                select(ShippingWarehouse)
                .where(
                    and_(
                        ShippingWarehouse.shipping_id == shipping.id,
                        ShippingWarehouse.warehouse_id == status.warehouse_id
                    )
                )
            )
            shipping_warehouses = sw_query.scalars().all()
            if status.warehouse_id == shipping.end_warehouse_id or all(sw.is_visited for sw in shipping_warehouses):
                await db.execute(update(Shipping).where(Shipping.id == shipping.id).values(status=ShippingStatus.FINISHED.value))
                await db.execute(update(ShippingRespond).where(and_(ShippingRespond.shipping_id == shipping.id, ShippingRespond.respond_status == ShippingRespondStatus.CONFIRMED.value)).values(respond_status=ShippingRespondStatus.FINISHED.value))
        await db.execute(update(OrderItems).where(OrderItems.id == order_item.id).values(status=OrderStatus.ARRIVED_TO_DESTINATION.value, warehouse_id=status.warehouse_id))
        await action_history_service.add_action(ActionHistoryCreate(order_item_id=order_item.id, warehouse_manager_id=user.id, warehouse_id=warehouse.id, action_code=ActionCode.ARRIVED_TO_DESTINATION), db)
        await db.commit()
        is_all_items_accepted = True
        for item in order.order_items:
            if item.status != OrderStatus.ARRIVED_TO_DESTINATION.value:
                is_all_items_accepted = False
                break
        if is_all_items_accepted:
            await db.execute(update(Orders).where(Orders.id == order.id).values(order_status=OrderStatus.ARRIVED_TO_DESTINATION.value, warehouse_id=warehouse.id, destination_warehouse_id=warehouse.id))
            await action_history_service.add_action(ActionHistoryCreate(order_id=order.id, warehouse_manager_id=user.id, warehouse_id=warehouse.id, action_code=ActionCode.ARRIVED_TO_DESTINATION), db)
        await db.commit()
        return {"detail": "Order item status updated"}

    async def set_as_in_transit(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        order_item = await db.execute(select(OrderItems).where(OrderItems.id == id))
        order_item = order_item.scalar_one_or_none()
        if order_item is None:
            raise HTTPException(status_code=404, detail="Order item not found")
        await db.execute(update(OrderItems).where(OrderItems.id == id).values(status=OrderStatus.IN_TRANSIT.value, warehouse_id=None))
        await db.commit()
        await action_history_service.add_action(ActionHistoryCreate(order_item_id=id, action_code=ActionCode.IN_TRANSIT, manager_id=user.id), db)
        return order_item

    async def set_as_partial_in_transit(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        order_item = await db.execute(select(OrderItems).where(OrderItems.id == id))
        order_item = order_item.scalar_one_or_none()
        if order_item is None:
            raise HTTPException(status_code=404, detail="Order item not found")
        await db.execute(update(OrderItems).where(OrderItems.id == id).values(status=OrderStatus.PARTIALLY_IN_TRANSIT.value))
        await db.commit()
        await action_history_service.add_action(ActionHistoryCreate(order_item_id=id, action_code=ActionCode.PARTIALLY_IN_TRANSIT, manager_id=user.id), db)
        return order_item

    def paginate(self, order_items, page: int, limit: int):
        return order_items.offset((page - 1) * limit).limit(limit)

    async def get_paginated_order_items_by_order_id(self, order_id: int, db: AsyncSession = Depends(get_db), page: int = 1, limit: int = 10) -> OrderItemsPaginated:
        filtered_order_items = select(OrderItems).where(
            OrderItems.order_id == order_id)
        paginated_order_items = self.paginate(
            filtered_order_items, page, limit)
        query = await db.execute(paginated_order_items)
        order_items = query.scalars().all()
        total = await db.execute(filtered_order_items)
        total = len(total.scalars().all())
        pages_number = total // limit
        if total % limit != 0:
            pages_number += 1
        return OrderItemsPaginated(
            page=page,
            pages_number=pages_number,
            total=total,
            limit=limit,
            data=order_items
        )


class OrderService(BaseDao):
    class_name = Orders

    async def create_order(self, payload: OrdersCreateSchemas, db: AsyncSession = Depends(get_db)):
        order_status = OrderStatus.CREATED.value
        unique_order_id = await Orders.generate_unique_id(db)
        order = Orders(
            id=unique_order_id,
            description=payload.description,
            warehouse_id=payload.warehouse_id,
            direction_id=payload.direction_id,
            sender_address=payload.sender_address,
            receiver_address=payload.receiver_address,
            courier=payload.courier,
            order_status=order_status,
            total_weight=payload.total_weight,
            total_volume=payload.total_volume,
            sender_fio=payload.sender_fio,
            sender_phone=payload.sender_phone,
            receiver_fio=payload.receiver_fio,
            receiver_phone=payload.receiver_phone,
            district_id=payload.district_id,
            destination_warehouse_id=payload.destination_warehouse_id,
            expenses_price=payload.expenses_price,
            start_warehouse_id=payload.start_warehouse_id,
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        payment = Payment(
            order_id=order.id,
            payment_status=PaymentStatus.NOT_PAID.value,
            payment_type=payload.payment.payment_type.value if payload.payment else None,
            payer_type=payload.payment.payer_type.value if payload.payment else None,
            amount=payload.payment.amount if payload.payment else 0,
            currency=payload.payment.currency.value if payload.payment else Currency.KZT.value,
            bin=payload.payment.bin if payload.payment else "",
            comment=payload.payment.comment if payload.payment else None
        )
        db.add(payment)
        order.payment = payment
        await db.commit()
        if payload.expenses and len(payload.expenses) > 0:
            for expense in payload.expenses:
                model = Expense
                query = await db.execute(select(model).where(model.id == expense))
                data = query.scalar_one_or_none()
                if not data:
                    continue
                else:
                    order.expenses.append(data)
        await db.commit()
        await action_history_service.add_action(ActionHistoryCreate(order_id=order.id, action_code=ActionCode.CREATED), db)
        return await nested_serializer.serialize_by_id(order.id, db)

    def paginate_orders(self, orders, page: int, limit: int):
        return orders.offset((page - 1) * limit).limit(limit)

    def generate_otp_code(self):
        return ''.join((random.choice('0123456789') for i in range(6)))

    def filter_orders(
            self,
            orders,
            warehouse_id: list[int] = None,
            direction_id: list[int] = None,
            transportation_type: list[TransportationType] = None,
            start_date: date = None,
            end_date: date = None,
            today: bool = None,
            all_time: bool = None,
            sort_by: str = None,
            sort_order: SortOrder = SortOrder.ASC,
            shipping_id: int = None) -> list[Orders]:
        if warehouse_id is not None:
            orders = orders.where(Orders.warehouse_id.in_(warehouse_id))
        if shipping_id is not None:
            orders = orders.join(Shipping, Orders.shippings).filter(
                Shipping.id == shipping_id)
        if direction_id is not None:
            orders = orders.where(Orders.direction_id.in_(direction_id))
        if start_date is not None:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            orders = orders.where(Orders.created_at >= start_datetime)
        if end_date is not None:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            orders = orders.where(Orders.created_at <= end_datetime)
        if transportation_type is not None:
            orders = orders.join(Directions).where(Directions.transportation_type.in_(
                [transportation_type.value for transportation_type in transportation_type]))
        if today is not None:
            orders = orders.where(Orders.created_at >= date.today())
        if all_time is not None:
            orders = orders.where(Orders.created_at <= date.today())
        if sort_by is not None:
            if sort_order == SortOrder.ASC:
                orders = orders.order_by(asc(getattr(Orders, sort_by)))
            else:
                orders = orders.order_by(desc(getattr(Orders, sort_by)))
        else:
            if sort_order == SortOrder.ASC:
                orders = orders.order_by(asc(Orders.created_at))
            else:
                orders = orders.order_by(desc(Orders.created_at))
        return orders

    def search_orders(self, orders, search: str = None):
        if search and not search.isspace():
            arrival_city = aliased(City)
            departure_city = aliased(City)
            orders = orders.join(Directions).join(
                arrival_city,
                arrival_city.id == Directions.arrival_city_id).join(
                departure_city,
                departure_city.id == Directions.departure_city_id).where(
                or_(
                    arrival_city.name.ilike(f"%{search}%"),
                    departure_city.name.ilike(f"%{search}%"),
                    Orders.sender_fio.ilike(f"%{search}%"),
                    Orders.receiver_fio.ilike(f"%{search}%"),
                    Orders.sender_phone.ilike(f"%{search}%"),
                    Orders.receiver_phone.ilike(f"%{search}%"),
                    cast(Orders.id, String).ilike(f"%{search}%")
                ))
        return orders

    async def get_orders_paginated(self, user: UserViewSchemas, db: AsyncSession = Depends(get_db),
                                   status: list[OrderStatus] = None, warehouse_id: list[int] = None,
                                   direction_id: list[int] = None, transportation_type: list[TransportationType] = None,
                                   start_date: date = None, end_date: date = None, page: int = 1, limit: int = 10,
                                   sort_by: str = None, sort_order: SortOrder = None, today: bool = None,
                                   all_time: bool = None, search: str = None, shipping_id: int = None) -> OrderPaginated:
        main_query = select(Orders).options(
            selectinload(
                Orders.direction), selectinload(
                Orders.warehouse), selectinload(
                Orders.payment))
        if status is not None:
            orders_filtered_by_status = main_query.where(Orders.order_status.in_(
                [status_group.value for status_group in status]))
        else:
            orders_filtered_by_status = main_query
        filtered_orders = self.filter_orders(
            orders_filtered_by_status,
            warehouse_id,
            direction_id,
            transportation_type,
            start_date,
            end_date,
            today,
            all_time,
            sort_by,
            sort_order,
            shipping_id)
        if (await if_user_has_permissions(db, user.id, [Permission.DELIVER_ORDER])):
            city_id = user.city
            warehouses = await db.execute(select(Warehouse).where(Warehouse.city == city_id))
            warehouses = warehouses.scalars().all()
            warehouse_ids = [warehouse.id for warehouse in warehouses]
            filtered_orders = filtered_orders.where(
                or_(
                    and_(
                        Orders.order_status == OrderStatus.ARRIVED_TO_DESTINATION.value,
                        Orders.destination_warehouse_id.in_(warehouse_ids)),
                    and_(
                        Orders.order_status == OrderStatus.DELIVERING_TO_RECIPIENT.value,
                        Orders.courier == user.id),
                    and_(
                        Orders.order_status == OrderStatus.ASSIGNED_TO_COURIER.value,
                        Orders.courier == user.id),
                    and_(Orders.order_status == OrderStatus.COURIER_DELIVERING_TO_WAREHOUSE.value,
                         Orders.courier == user.id),
                    and_(Orders.order_status == OrderStatus.DELIVERED.value,
                         Orders.courier == user.id)))
        elif (await if_user_has_permissions(db, user.id, [Permission.ACCEPT_ORDER_TO_WAREHOUSE])):
            filtered_orders = filtered_orders.where(
                or_(
                    Orders.warehouse_id == user.warehouse_id,
                    and_(Orders.order_status == OrderStatus.CLIENT_DELIVERING_TO_WAREHOUSE.value,
                         Orders.start_warehouse_id == user.warehouse_id),
                    and_(Orders.order_status == OrderStatus.CLIENT_DELIVERING_TO_WAREHOUSE.value,
                         Orders.warehouse_id == user.warehouse_id),
                    and_(Orders.order_status == OrderStatus.COURIER_DELIVERING_TO_WAREHOUSE.value,
                         Orders.warehouse_id == user.warehouse_id))
            )
        elif (await if_user_has_permissions(db, user.id, [Permission.UPDATE_PAYMENT_STATUS_UL])):
            filtered_orders = filtered_orders.join(Payment).where(
                Payment.payer_type == PayerType.UL.value)
        initial_orders = self.search_orders(filtered_orders, search)
        orders = await db.execute(self.paginate_orders(initial_orders, page, limit))
        orders = orders.scalars().all()
        tasks = [nested_serializer.serialize_by_id_short(
            order) for order in orders]
        response = await asyncio.gather(*tasks)
        total_orders = (await db.execute(filtered_orders)).scalars().all()
        pages_number = len(total_orders) // limit
        if len(total_orders) % limit != 0:
            pages_number += 1
        return OrderPaginated(
            page=page,
            limit=limit,
            total=len(total_orders),
            pages_number=pages_number,
            data=response)

    async def get_order(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)) -> OrderViewSchemas:
        return await nested_serializer.serialize_by_id(id, db, user)

    async def get_client_order(self, id: int, db: AsyncSession = Depends(get_db)) -> OrderViewSchemas:
        return await nested_serializer.serialize_by_id(id, db)

    async def get_order_by_qr_code(self, qr_code: str, db: AsyncSession = Depends(get_db)) -> OrderViewSchemas:
        query = await db.execute(select(OrderItems).where(OrderItems.qr_code_hash == qr_code))
        order_item = query.scalar_one_or_none()
        if order_item is None:
            raise HTTPException(status_code=404, detail="Order item not found")
        order = await db.execute(select(Orders).where(Orders.id == order_item.order_id))
        order = order.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return await nested_serializer.serialize_by_id(order.id, db)

    async def delete_orders(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        order_items = delete(OrderItems).where(OrderItems.order_id == id)
        await db.execute(order_items)
        payment = delete(Payment).where(Payment.order_id == id)
        await db.execute(payment)
        order = delete(Orders).where(Orders.id == id)
        await db.execute(order)
        await db.commit()

    async def update_order(self, id: int, payload: OrderUpdateSchemas, user: UserViewSchemas, db: AsyncSession = Depends(get_db)) -> OrderViewSchemas:
        query = await db.execute(select(Orders).where(Orders.id == id))
        order = query.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        if payload.payment:
            # TODO: this is code when courier accepts order, measure the weight and volume and calculate the tarif
            # Need to refactor this code
            payment = await db.execute(select(Payment).where(Payment.order_id == id))
            payment = payment.scalar_one_or_none()
            if payment is None:
                raise HTTPException(
                    status_code=404, detail="Payment not found")
            await db.execute(update(Payment).where(Payment.order_id == id).values(
                amount=payload.payment.amount,
                currency=payload.payment.currency.value,
                payment_type=payload.payment.payment_type.value if payload.payment.payment_type else None,
                comment=payload.payment.comment if payload.payment.comment else None,
                payer_type=payload.payment.payer_type.value if payload.payment.payer_type else None,
                bin=payload.payment.bin
            ))
        if payload.expenses:
            for item in payload.expenses:
                expense = await db.execute(select(Expense).where(Expense.id == item))
                data = expense.scalar_one_or_none()
                if data:
                    order.expenses.append(data)
        status = None
        if order.order_status in [
                OrderStatus.CREATED.value,
                OrderStatus.CLIENT_DELIVERING_TO_WAREHOUSE.value,
                OrderStatus.ASSIGNED_TO_COURIER.value]:
            status = await self.accept_order(payload, user, order.id, db)
        else:
            status = order.order_status
        warehouse_id = None
        if (await if_user_has_permissions(db, user.id, [Permission.ACCEPT_ORDER_TO_WAREHOUSE])):
            warehouse_id = user.warehouse_id
        else:
            warehouse_id = payload.warehouse_id
        await db.execute(update(Orders).where(Orders.id == id).values(
            order_status=status,
            description=payload.description,
            delivery_type=payload.delivery_type.value,
            cargo_pickup_type=payload.cargo_pickup_type.value,
            warehouse_id=warehouse_id,
            direction_id=payload.direction_id,
            sender_address=payload.sender_address,
            receiver_address=payload.receiver_address,
            courier=payload.courier,
            district_id=payload.district_id,
            total_weight=payload.total_weight,
            total_volume=payload.total_volume,
            sender_fio=payload.sender_fio,
            sender_phone=payload.sender_phone,
            receiver_fio=payload.receiver_fio,
            receiver_phone=payload.receiver_phone,
            insurance=payload.insurance,
            destination_warehouse_id=payload.destination_warehouse_id,
            expenses_price=payload.expenses_price,
            start_warehouse_id=payload.start_warehouse_id
        ))
        await db.commit()
        return await nested_serializer.serialize_by_id(id, db)

    async def calculate_extra_costs(self, cargo_pickup_type: str, delivery_type: str, total_weight: int,
                                    total_volume: int, db: AsyncSession = Depends(get_db)) -> (int, int):
        extra_cargo_cost = 0
        extra_delivery_cost = 0
        tarif_weight = (await db.execute(select(Tarifs).filter_by(
            calculation_type=CalculationType.DELIVERY_WEIGHT.value,
            amount=math.ceil(total_weight)))).scalar_one_or_none()
        tarif_volume = (await db.execute(select(Tarifs).filter_by(
            calculation_type=CalculationType.DELIVERY_VOLUME.value,
            amount=math.ceil(total_volume)))).scalar_one_or_none()
        max_price_for_delivery = max(tarif_weight.price if tarif_weight else 0,
                                     tarif_volume.price if tarif_volume else 0)
        if cargo_pickup_type == DeliveryType.DELIVERY.value:
            extra_cargo_cost += max_price_for_delivery
        if delivery_type == DeliveryType.DELIVERY.value:
            extra_delivery_cost += max_price_for_delivery
        return extra_cargo_cost, extra_delivery_cost

    async def calculate_tarif(self, db: AsyncSession = Depends(get_db), direction_id=0, total_weight: int = 0,
                              total_volume: int = 0, cargo_pickup_type: str = None, delivery_type: str = None):

        extra_cargo_cost, extra_delivery_cost = await self.calculate_extra_costs(cargo_pickup_type, delivery_type, total_weight, total_volume, db)

        extra_costs = {'weight': 0, 'handling': 0}
        limit_prices = {'weight': 0, 'handling': 0}

        calculation_types = ["WEIGHT", "HANDLING"]

        # Fetch and set limit prices
        for calc_type in calculation_types:
            try:
                limit_tarif = await db.execute(select(Tarifs).filter_by(
                    calculation_type=calc_type, direction_id=direction_id, is_limit=True))
                limit_tarif = limit_tarif.scalar_one().price
                limit_prices[calc_type.lower()] = limit_tarif
            except NoResultFound:
                pass  # Defaults are already set to 0
        if total_weight > 100:
            extra_costs['weight'] = (
                total_weight - 100) * limit_prices['weight']
            extra_costs['handling'] = (
                total_weight - 100) * limit_prices['handling']
            total_weight = 100
        try:
            # Fetch tariffs based on updated totals
            tariffs = {calc_type: (await db.execute(select(Tarifs).filter_by(
                calculation_type=calc_type,
                amount=math.ceil(total_weight),
                direction_id=direction_id))).scalar_one() for calc_type in calculation_types}
        except NoResultFound:
            raise HTTPException(
                status_code=400,
                detail=f"Укажите ценовой диапазон для текущего направления {direction_id} и weight_amount {total_weight}")
        volume_tarifs = await db.execute(select(Tarifs).filter_by(
            calculation_type="VOLUME",
            direction_id=direction_id))
        volume_tarifs = volume_tarifs.scalars().first()
        # Calculate the tariff price
        tarif_price = max(volume_tarifs.price * total_volume if volume_tarifs else 0,
                          tariffs[CalculationType.WEIGHT].price) + tariffs[CalculationType.HANDLING].price

        return tarif_price + sum(extra_costs.values()) + extra_cargo_cost + extra_delivery_cost

    async def accept_order(self, payload: OrderUpdateSchemas, user: UserViewSchemas, order_id: int, db: AsyncSession = Depends(get_db)):
        if (await if_user_has_permissions(db, user.id, [Permission.DELIVER_ORDER])):
            status = OrderStatus.COURIER_DELIVERING_TO_WAREHOUSE.value
        elif (await if_user_has_permissions(db, user.id, [Permission.ACCEPT_ORDER_TO_WAREHOUSE])):
            status = OrderStatus.ACCEPTED_TO_WAREHOUSE.value
        elif payload.cargo_pickup_type.value == DeliveryType.PICKUP.value:
            status = OrderStatus.CLIENT_DELIVERING_TO_WAREHOUSE.value
        elif payload.cargo_pickup_type.value == DeliveryType.DELIVERY.value:
            status = OrderStatus.ASSIGNED_TO_COURIER.value
            await notification_service.send_notification(user_id=payload.courier, notification_code=NotificationCode.COURIER_NEW_ORDER)
        return status

    async def update_payment_order(self, id: int, payment_payload: PaymentUpdateSchemas, user: UserViewSchemas, db: AsyncSession = Depends(get_db)) -> PaymentUpdateSchemas:
        payment = update(Payment).where(
            Payment.order_id == id).values(
                amount=payment_payload.amount,
                currency=payment_payload.currency,
                payment_type=payment_payload.payment_type.value,
                payer_type=payment_payload.payer_type.value,
                bin=payment_payload.bin
        )
        await db.execute(payment)
        await db.commit()
        return payment_payload

    async def get_order_or_404(self, id: int, db: AsyncSession = Depends(get_db)) -> Orders:
        query = await db.execute(select(Orders).where(Orders.id == id))
        order = query.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    async def set_as_paid(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        await db.execute(update(Payment).where(Payment.order_id == id).values(payment_status=PaymentStatus.PAID.value))
        await db.commit()
        return await nested_serializer.serialize_by_id(id, db)

    async def set_as_not_paid(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        await db.execute(update(Payment).where(Payment.order_id == id).values(payment_status=PaymentStatus.NOT_PAID.value))
        await db.commit()
        return await nested_serializer.serialize_by_id(id, db)

    async def set_as_delivered(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        await db.execute(update(Orders).where(Orders.id == id).values(order_status=OrderStatus.DELIVERED.value))
        await db.commit()
        return await nested_serializer.serialize_by_id(id, db)

    async def set_as_cancelled(self, id: int, payload: CancelledOrder, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        order: Orders = await self.get_order_or_404(id, db)
        await db.execute(update(Orders).where(Orders.id == id).values(order_status=OrderStatus.CANCELLED.value, order_status_previous=order.order_status, cancellation_reason=payload.reason))
        await db.commit()
        return await nested_serializer.serialize_by_id(id, db)

    async def set_as_accepted_to_warehouse(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        order = await db.execute(select(Orders).where(Orders.id == id))
        order = order.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        await db.execute(update(Orders).where(Orders.id == id).values(order_status=OrderStatus.ACCEPTED_TO_WAREHOUSE.value))
        await db.commit()
        return await nested_serializer.serialize_by_id(id, db)

    async def set_as_courier_delivering_to_warehouse(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        order = await db.execute(select(Orders).where(Orders.id == id))
        order = order.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        await db.execute(update(Orders).where(Orders.id == id).values(order_status=OrderStatus.COURIER_DELIVERING_TO_WAREHOUSE.value))
        await db.commit()
        await action_history_service.add_action(ActionHistoryCreate(order_id=id, courier_id=user.id, action_code=ActionCode.COURIER_DELIVERING_TO_WAREHOUSE), db)
        return await nested_serializer.serialize_by_id(id, db)

    async def set_as_in_transit(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        order = await db.execute(select(Orders).where(Orders.id == id))
        order = order.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        await db.execute(update(Orders).where(Orders.id == id).values(order_status=OrderStatus.IN_TRANSIT.value, warehouse_id=None))
        await db.commit()
        await action_history_service.add_action(ActionHistoryCreate(order_id=id, action_code=ActionCode.IN_TRANSIT, manager_id=user.id), db)
        return await nested_serializer.serialize_by_id(id, db)

    async def set_as_partial_in_transit(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        order = await db.execute(select(Orders).where(Orders.id == id))
        order = order.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        await db.execute(update(Orders).where(Orders.id == id).values(order_status=OrderStatus.PARTIALLY_IN_TRANSIT.value))
        await db.commit()
        await action_history_service.add_action(ActionHistoryCreate(order_id=id, action_code=ActionCode.PARTIALLY_IN_TRANSIT, manager_id=user.id), db)
        return await nested_serializer.serialize_by_id(id, db)

    async def set_as_not_delivered(self, id: int, payload: NotDeliveredOrder, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        await db.execute(update(Orders).where(Orders.id == id).values(order_status=OrderStatus.NOT_DELIVERED.value, not_delivered_reason=payload.reason))
        await db.commit()
        order_items = await db.execute(select(OrderItems).where(OrderItems.order_id == id))
        order_items = order_items.scalars().all()
        for order_item in order_items:
            await db.execute(update(OrderItems).where(OrderItems.id == order_item.id).values(status=OrderStatus.NOT_DELIVERED.value))
            await action_history_service.add_action(ActionHistoryCreate(order_item_id=order_item.id, action_code=ActionCode.NOT_DELIVERED, courier_id=user.id), db)
        return await nested_serializer.serialize_by_id(id, db)

    async def set_as_delivering_to_recipient(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        await db.execute(update(Orders).where(Orders.id == id).values(order_status=OrderStatus.DELIVERING_TO_RECIPIENT.value))
        await db.commit()
        return await nested_serializer.serialize_by_id(id, db)

    async def send_otp_code_for_signing(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)) -> SendOTPSigning:
        query = await db.execute(select(Orders).options(selectinload(Orders.direction)).where(Orders.id == id))
        order: Orders = query.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        otp_code = self.generate_otp_code()
        # TODO: needs to handle as a database transaction and send sms code
        # If sms code is sent successfully then save otp code to database
        # If sms code is not sent then rollback the transaction
        if settings.ENVIRONMENT != Environment.LOCAL:
            notification_service.send_sms(
                phone=order.sender_phone, sms_code=SmsCode.PUBLIC_OFFER, code=otp_code)
            template = NOTIFICATION_TEMPLATES[SmsCode.TRACKING_TEMPLATE]
            whatsapp_client.send_sms(
                order.sender_phone, template.message.format(
                    url=f'{settings.FRONTEND_URL}/orders/public/{order.id}'))
            whatsapp_client.send_sms(
                order.receiver_phone, template.message.format(
                    url=f'{settings.FRONTEND_URL}/orders/public/{order.id}'))
        otp_signing_code = OTPSigningCode(
            user_id=user.id,
            code=otp_code,
            phone=order.sender_phone,
            order_id=id,
            otp_type=OTPType.PUBLIC_OFFER.value)
        db.add(otp_signing_code)
        await db.commit()
        await self.generate_waiver_agreement(order, otp_code, True, db)
        return SendOTPSigning(phone=order.receiver_phone, code=otp_code)

    async def accept_public_offer(self, id: int, payload: SignOrderOTP, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        query = await db.execute(select(Orders).where(Orders.id == id))
        order = query.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        otp_signing_code = await db.execute(select(OTPSigningCode).where(OTPSigningCode.code == payload.code))
        otp_signing_code = otp_signing_code.scalar_one_or_none()
        if otp_signing_code is None:
            raise HTTPException(status_code=404, detail="OTP code not found")
        if otp_signing_code.order_id != id:
            raise PermissionDenied()
        await db.execute(update(Orders).where(Orders.id == id).values(is_public_offer_accepted=True))
        await db.execute(update(OTPSigningCode).where(OTPSigningCode.id == otp_signing_code.id).values(is_used=True))
        await db.commit()
        return await nested_serializer.serialize_by_id(id, db)

    # TODO: candidate for deletion
    async def get_waiver_agreement(self, id: int, db: AsyncSession = Depends(get_db)) -> StreamingResponse:
        query = await db.execute(select(Orders).where(Orders.id == id))
        order = query.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        file_path = os.path.join(os.getcwd(), "src/waiver_agreement.pdf")
        return StreamingResponse(open(file_path, "rb"), media_type="application/pdf")

    async def convert_docx_to_pdf(self, new_doc_path: str, new_pdf_path: str):
        cmd = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(new_pdf_path),
               new_doc_path]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open(new_pdf_path, 'rb') as pdf_file:
            file_stream = io.BytesIO(pdf_file.read())
        return file_stream

    async def generate_waiver_agreement(self, order: Orders, otp_code: str, is_public_offer: bool, db: AsyncSession = Depends(get_db)):
        doc_type = 'public_offer' if is_public_offer else 'waiver_agreement'
        if order.direction.transportation_type.value == TransportationType.AIR:
            doc_path = "public_offer_avia.docx" if is_public_offer else "waiver_agreement_avia.docx"
        else:
            doc_path = "public_offer_not_avia.docx" if is_public_offer else "waiver_agreement_not_avia.docx"
        doc = Document(doc_path)
        sended_date = date.today().strftime('%m/%d/%Y')
        replacements = {
            '{{sender_fio}}': order.sender_fio,
            '{{order_id}}': str(order.id),
            '{{sended_date}}': sended_date,
            '{{receiver_fio}}': order.receiver_fio,
            '{{otp_code}}': otp_code,
            '{{sender_phone}}': order.sender_phone,
            '{{receiver_phone}}': order.receiver_phone
        }
        for paragraph in doc.paragraphs:
            for key, value in replacements.items():
                if key in paragraph.text:
                    paragraph.text = paragraph.text.replace(key, value)

        new_doc_path = f'{doc_type}_agreement_{order.id}_{otp_code}.docx'
        doc.save(new_doc_path)
        new_pdf_path = f'{doc_type}_agreement_{order.id}_{otp_code}.pdf'
        file_stream = await self.convert_docx_to_pdf(new_doc_path, new_pdf_path)
        file_s3 = await file_service.upload_file(new_pdf_path, file_stream)
        os.remove(new_doc_path)
        setattr(order, 'public_offer_url' if is_public_offer else 'waiver_agreement_url',
                file_s3['file_path'])
        await db.commit()

    async def send_otp_code_for_waiver_agreement(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)) -> SendOTPSigning:
        query = await db.execute(select(Orders).options(selectinload(Orders.direction)).where(Orders.id == id))
        order: Orders = query.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        otp_code = self.generate_otp_code()
        if settings.ENVIRONMENT != Environment.LOCAL:
            notification_service.send_sms(
                phone=order.receiver_phone, sms_code=SmsCode.WAIVER_AGREEMENT, code=otp_code)
        otp_signing_code = OTPSigningCode(
            user_id=user.id,
            code=otp_code,
            phone=order.receiver_phone,
            order_id=id,
            otp_type=OTPType.WAIVER_AGREEMENT.value)
        db.add(otp_signing_code)
        await db.commit()
        await self.generate_waiver_agreement(order, otp_code, False, db)
        return SendOTPSigning(phone=order.receiver_phone, code=otp_code)

    async def accept_waiver_agreement(self, id: int, payload: SignOrderOTP, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        query = await db.execute(select(Orders).options(
            selectinload(Orders.payment)
        ).where(Orders.id == id))
        order: Orders = query.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        otp_signing_code = await db.execute(select(OTPSigningCode).where(OTPSigningCode.code == payload.code))
        otp_signing_code = otp_signing_code.scalar_one_or_none()
        if otp_signing_code is None:
            raise HTTPException(status_code=404, detail="OTP code not found")
        if otp_signing_code.order_id != id:
            raise PermissionDenied()
        if order and order.order_status == OrderStatus.DELIVERING_TO_RECIPIENT and order.courier:
            new_association = UsersOrders(
                user_id=order.courier,
                order_id=order.id,
                status=OrderStatus.DELIVERED.value
            )
            db.add(new_association)
        await db.execute(update(Orders).where(Orders.id == id).values(is_waiver_agreement_accepted=True))
        await db.execute(update(OTPSigningCode).where(OTPSigningCode.id == otp_signing_code.id).values(is_used=True))
        order.order_status = OrderStatus.DELIVERED.value
        order.warehouse_id = None
        await action_history_service.add_action(ActionHistoryCreate(order_id=id, action_code=ActionCode.DELIVERED, courier_id=user.id), db)
        order_items = await db.execute(select(OrderItems).where(OrderItems.order_id == id))
        order_items = order_items.scalars().all()
        for order_item in order_items:
            order_item.status = OrderStatus.DELIVERED.value
            await action_history_service.add_action(ActionHistoryCreate(order_item_id=order_item.id, action_code=ActionCode.DELIVERED, courier_id=user.id), db)
        if order.courier:
            await db.execute(
                update(Users).where(Users.id == order.courier).values(
                    total_profit=Users.total_profit + order.payment.amount))
            courier = await db.execute(select(Users).where(Users.id == order.courier))
            courier = courier.scalar_one_or_none()
            if courier:
                courier.delivered_orders += 1
        await db.commit()
        return await nested_serializer.serialize_by_id(id, db)

    async def resume_order(self, id: int, user: UserViewSchemas, db: AsyncSession = Depends(get_db)):
        order: Orders = await self.get_order_or_404(id, db)
        if order.order_status_previous:
            await db.execute(update(Orders).where(Orders.id == id).values(order_status=order.order_status_previous, order_status_previous=None))
            await db.commit()
        elif not order.order_status_previous:
            raise HTTPException(
                status_code=400, detail="Order status previous not found")
        return await nested_serializer.serialize_by_id(id, db)

    async def calculate_expenses(self, ids: list, db: AsyncSession = Depends(get_db)) -> ExpensesTotalPrice:
        if not ids:
            return ExpensesTotalPrice(expenses_total_price=0)
        try:
            result = await db.execute(
                select(func.sum(Expense.price)).where(Expense.id.in_(ids))
            )
            expenses_total_price = result.scalar_one() or Decimal('0.00')
        except NoResultFound:
            expenses_total_price = Decimal('0.00')
        return ExpensesTotalPrice(expenses_total_price=expenses_total_price)

    async def total_amount(self, payload: TotalAmountOrder, db: AsyncSession = Depends(get_db)) -> TotalAmount:
        total_price = await self.calculate_tarif(db=db, total_weight=payload.total_weight,
                                                 total_volume=payload.total_volume, direction_id=payload.direction_id,
                                                 cargo_pickup_type=payload.cargo_pickup_type, delivery_type=payload.delivery_type)
        total_amount = payload.expenses_price + total_price
        return TotalAmount(total_amount=total_amount)

    def if_all_orders_are_taken(self, order_items_ids, payload_orders_items_id) -> bool:
        return all(item_id in payload_orders_items_id for item_id in order_items_ids)

    async def add_order_items_for_delivery(self, payload: CourierDeliverySchema, user: UserViewSchemas,
                                           db: AsyncSession):
        order_items_query = await db.execute(select(OrderItems).where(OrderItems.id.in_(payload.orders_items_id)))
        order_items_in_payload = order_items_query.scalars().all()

        orders_to_items = defaultdict(list)
        for item in order_items_in_payload:
            orders_to_items[item.order_id].append(item)

        for order_id, items in orders_to_items.items():
            current_order_query = await db.execute(select(Orders).where(Orders.id == order_id))
            current_order = current_order_query.scalar_one_or_none()

            if not current_order:
                continue

            all_order_items_query = await db.execute(select(OrderItems).where(OrderItems.order_id == order_id))
            all_order_items = all_order_items_query.scalars().all()

            all_order_items_ids = {item.id for item in all_order_items}
            payload_order_items_ids = {item.id for item in items}

            if not all_order_items_ids.issubset(payload_order_items_ids):
                raise HTTPException(
                    status_code=400, detail=f"Not all order_items from order {order_id} are included.")

            if current_order.order_status == OrderStatus.ACCEPTED_TO_WAREHOUSE.value:
                new_status = OrderStatus.COURIER_DELIVERING_TO_WAREHOUSE.value
            elif current_order.order_status == OrderStatus.ARRIVED_TO_DESTINATION.value:
                new_status = OrderStatus.DELIVERING_TO_RECIPIENT.value
            else:
                continue

            current_order.order_status = new_status
            current_order.courier = user.id

            for item in items:
                await db.execute(
                    update(OrderItems)
                    .where(OrderItems.id == item.id)
                    .values(status=new_status)
                )
                await action_history_service.add_action(
                    ActionHistoryCreate(order_item_id=item.id, action_code=new_status, courier_id=user.id), db)
        await db.commit()
        return {"detail": "Order items status updated"}

    async def upload_photos_to_order(self, order_id: int, files: list[UploadFile], db: AsyncSession):
        for file in files:
            file_s3 = await file_service.upload_file(file.filename, file.file)
            order_photo = OrderPhoto(
                order_id=order_id,
                photo=file_s3['file_path']
            )
            db.add(order_photo)
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e
        finally:
            await db.close()
        return {"detail": "Photos uploaded successfully."}


order_service = OrderService()
order_item_service = OrderItemService()
