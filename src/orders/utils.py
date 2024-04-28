from datetime import date, datetime
from io import BytesIO
from typing import List

from fastapi import Depends
from openpyxl.workbook import Workbook
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.action_history.models import ActionCode, ActionHistory
from src.action_history.schemas import ActionHistoryShortOut
from src.common.models import SortOrder
from src.database import get_db
from src.directions.models import Directions, TransportationType
from src.directions.schemas import DirectionOut
from src.expenses.schemas import ExpenseViewSchemas
from src.geography.models import City, District
from src.geography.schemas import CityOut, DistrictShortViewSchemas
from src.orders.models import (OrderItems, Orders, OrderStatus, Payment,
                               PaymentStatus)
from src.orders.schemas import (OrderItemsOut, OrderViewSchemas, PayerType,
                                PaymentOut, OrderPhotosOutSchemas, PaymentType, OrderViewSchemasShort)
from src.users.models import Users
from src.users.perms import if_user_has_permissions
from src.users.schemas import Permission
from src.warehouse.models import Warehouse
from src.warehouse.schemas import WarehouseOutShort


class OrderViewSerialized:

    async def get_order_items(self, order: Orders, db: AsyncSession = Depends(get_db)) -> List[OrderItemsOut]:
        order_items = await db.execute(select(OrderItems).where(OrderItems.order_id == order.id))
        order_items = order_items.scalars().all()

        order_item_ids = [item.id for item in order_items]
        action_histories = await db.execute(
            select(ActionHistory).where(
                ActionHistory.order_item_id.in_(order_item_ids),
                ActionHistory.action_code == ActionCode.ARRIVED_TO_DESTINATION.value
            )
        )
        action_histories = action_histories.scalars().all()
        action_history_map = {history.order_item_id: history for history in action_histories}

        order_items_out = []
        for order_item in order_items:
            fine = 0
            action_history_order_item = action_history_map.get(order_item.id)
            if action_history_order_item:
                days_since_arrived = (datetime.now() - action_history_order_item.created_at).days
                if days_since_arrived > 3:
                    fine_days = days_since_arrived - 3
                    fine = 500 * fine_days
            order_items_out.append(OrderItemsOut(**{**dict(order_item.__dict__), "fine": fine}))
        return order_items_out

    async def serialize_by_id(self, id: int, db: AsyncSession = Depends(get_db), user: Users = None) -> OrderViewSchemas:
        order = await db.execute(select(Orders).where(Orders.id == id))
        order = order.scalar_one_or_none()

        warehouse = await db.execute(select(Warehouse).where(Warehouse.id == order.warehouse_id))
        warehouse = warehouse.scalars().first()
        warehouse_model = None
        if warehouse:
            warehouse_model = WarehouseOutShort(**warehouse.__dict__)

        start_warehouse = await db.execute(select(Warehouse).where(Warehouse.id == order.start_warehouse_id))
        start_warehouse = start_warehouse.scalars().first()

        destination_warehouse = await db.execute(select(Warehouse).where(Warehouse.id == order.destination_warehouse_id))
        destination_warehouse = destination_warehouse.scalars().first()

        direction = await db.execute(select(Directions).where(Directions.id == order.direction_id))
        direction = direction.scalars().first()

        arival_city = await db.execute(select(City).where(City.id == direction.arrival_city_id))
        arival_city = arival_city.scalars().first()

        departure_city = await db.execute(select(City).where(City.id == direction.departure_city_id))
        departure_city = departure_city.scalars().first()

        arrival_city_out = CityOut(**arival_city.__dict__)
        departure_city_out = CityOut(**departure_city.__dict__)

        direction_out = DirectionOut(id=direction.id,
                                     arrival_city=arrival_city_out,
                                     departure_city=departure_city_out,
                                     transportation_type=direction.transportation_type
                                     )

        payment = await db.execute(select(Payment).where(Payment.order_id == order.id))
        payment = payment.scalars().first()
        payment_model = PaymentOut(**payment.__dict__) if payment else None
        order_items_out = await self.get_order_items(order=order, db=db)
        order_photos_out = [OrderPhotosOutSchemas(**order_photo.__dict__) for order_photo in order.order_photo]

        expenses_out = []
        for expense in order.expenses:
            expenses_out.append(ExpenseViewSchemas(**expense.__dict__))

        action_history_out = []
        action_history = await db.execute(select(ActionHistory).where(ActionHistory.order_id == order.id))

        for action in action_history.scalars().all():
            action_history_out.append(ActionHistoryShortOut(**action.__dict__))
        district = await db.execute(select(District).where(District.id == order.district_id))
        district = district.scalar_one_or_none()
        district = None if not district else DistrictShortViewSchemas(
            id=district.id, name=district.name)
        is_payment_editable = await order.is_payment_editable(user, db) if user else False
        data = OrderViewSchemas(
            id=order.id,
            sender_address=order.sender_address,
            district=district,
            receiver_address=order.receiver_address,
            courier=order.courier,
            sender_fio=order.sender_fio,
            description=order.description,
            sender_phone=order.sender_phone,
            receiver_fio=order.receiver_fio,
            receiver_phone=order.receiver_phone,
            total_weight=order.total_weight,
            total_volume=order.total_volume,
            insurance=order.insurance,
            created_at=order.created_at,
            order_status=order.order_status,
            is_public_offer_accepted=order.is_public_offer_accepted,
            delivery_type=order.delivery_type,
            cargo_pickup_type=order.cargo_pickup_type,
            public_offer_url=order.public_offer_url,
            warehouse=warehouse_model,
            destination_warehouse=WarehouseOutShort(
                **destination_warehouse.__dict__) if destination_warehouse else None,
            start_warehouse=WarehouseOutShort(
                **start_warehouse.__dict__) if start_warehouse else None,
            payment=payment_model,
            direction=direction_out,
            order_items=order_items_out,
            order_items_number=len(order_items_out),
            expenses=expenses_out,
            action_histories=action_history_out,
            not_delivered_reason=order.not_delivered_reason,
            cancellation_reason=order.cancellation_reason,
            waiver_agreement_url=order.waiver_agreement_url,
            expenses_price=order.expenses_price,
            is_payment_editable=is_payment_editable,
            order_photos=order_photos_out
        )
        return data

    async def serialize_by_id_short(self, order: Orders) -> OrderViewSchemasShort:
        return OrderViewSchemasShort(
            id=order.id,
            sender_address=order.sender_address,
            receiver_address=order.receiver_address,
            sender_fio=order.sender_fio,
            sender_phone=order.sender_phone,
            receiver_fio=order.receiver_fio,
            receiver_phone=order.receiver_phone,
            order_items_number=len(order.order_items),
            created_at=order.created_at,
            order_status=order.order_status,
            direction=DirectionOut(**order.direction.__dict__) if order.direction else None,
            payment=PaymentOut(**order.payment.__dict__) if order.payment else None,
            warehouse=WarehouseOutShort(**order.warehouse.__dict__) if order.warehouse else None
        )


async def generate_excel_file(db: AsyncSession = Depends(get_db), user: str = None, status: list[OrderStatus] = None, warehouse_id: list[int] = None,
                              direction_id: list[int] = None, transportation_type: list[TransportationType] = None,
                              start_date: date = None, end_date: date = None,
                              sort_by: str = None, sort_order: SortOrder = None, today: bool = None,
                              all_time: bool = None, search: str = None):
    async with db.begin():
        from src.orders.service import order_service
        query = select(Orders).options(
            selectinload(Orders.warehouse),
            selectinload(Orders.payment),
            selectinload(Orders.direction)
        ).order_by(Orders.created_at.asc())
        if status is not None:
            query = query.where(Orders.order_status.in_(
                [status_group.value for status_group in status]))
        if user and (await if_user_has_permissions(db, user.id, [Permission.UPDATE_PAYMENT_STATUS_UL])):
            query = query.join(Payment).filter(Payment.payer_type == PayerType.UL.value)
        filtered_query = order_service.filter_orders(
            query,
            warehouse_id,
            direction_id,
            transportation_type,
            start_date,
            end_date,
            today,
            all_time,
            sort_by,
            sort_order)
        filtered_query = order_service.search_orders(filtered_query, search)
        filtered_result = await db.execute(filtered_query)
        filtered_orders = filtered_result.scalars().all()
        order_items_count_query = select(
            OrderItems.order_id,
            func.count().label('items_count')
        ).group_by(OrderItems.order_id)

        result = await db.execute(order_items_count_query)
        order_items_count = result.all()
    order_items_count_dict = {order_id: count for order_id, count in order_items_count}
    wb = Workbook()
    ws = wb.active
    ws.title = "Заказы"

    columns = [
        "ID",
        "Дата",
        "Откуда",
        "Отправитель",
        "Контакт отправителя",
        "Количество",
        "Вес",
        "Объем",
        "Сумма",
        "Упаковка",
        "Доставка",
        "Забор",
        "Куда",
        "Получатель",
        "Контакты получателя",
        "Тип отправки",
        "Тип оплаты",
        "Местонахождение",
        "Оплачено",
        "Сотрудник",
        "Характер груза"]
    ws.append(columns)
    for order in filtered_orders:
        payment_status = 'ДА' if order.payment and order.payment.payment_status == PaymentStatus.PAID.value else 'НЕТ'
        payment_type = None
        transportation_type = None
        if order.payment:
            if order.payment.payment_type == PaymentType.CASH.value:
                payment_type = 'Наличные'
            if order.payment.payment_type == PaymentType.ONLINE.value:
                payment_type = 'Онлайн'
        if order.direction:
            if order.direction.transportation_type == TransportationType.AIR.value:
                transportation_type = 'Самолет'
            if order.direction.transportation_type == TransportationType.RAIL.value:
                transportation_type = 'ЖД'
            if order.direction.transportation_type == TransportationType.ROAD.value:
                transportation_type = 'Фура'
        ws.append([
            order.id,
            order.created_at,
            order.direction.departure_city.name if order.direction else None,
            order.sender_fio,
            order.sender_phone,
            order_items_count_dict.get(order.id, 0),
            order.total_weight,
            order.total_volume,
            order.payment.amount if order.payment else 0,
            None,  # Упаковка
            None,  # Доставка
            None,  # Забор
            order.direction.arrival_city.name if order.direction else None,
            order.receiver_fio,
            order.receiver_phone,
            transportation_type,
            payment_type,
            f'{order.warehouse.name}, {order.warehouse.address}' if order.warehouse else None,
            payment_status,
            None,  # Сотрудник,
            order.description

        ])
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    return excel_file

nested_serializer = OrderViewSerialized()
