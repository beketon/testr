from collections import defaultdict
from datetime import date, datetime
from typing import List

from fastapi import Depends, Query
from sqlalchemy import func, or_, select, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.directions.models import TransportationType, Directions
from src.orders.models import Orders, Payment, OrderStatus
from src.orders.schemas import PaymentType
from src.shipping.models import Shipping
from src.statistics.schemas import (ORDER_GROUPS, OrdersStatistics,
                                    PaymentStatistics, ShippingStatistics,
                                    ShippingTypeCount, TotalOrdersCount,
                                    TotalVolume, TotalWeightSchema, CourierStatisticsSchema)
from src.statistics.utils import StatisticFilterUtils
from src.users.models import Users, auth_group_permission, Permission, UsersOrders
from src.users.schemas import Permission as PermissionSchema


class StatisticService:

    async def total_weight(self, db: AsyncSession = Depends(get_db), start_date: date = Query(None),
                           end_date: date = Query(None), direction_ids: List[int] = Query(None), transportation_type: TransportationType = Query(None)) -> TotalWeightSchema:
        model = Orders
        query = (select(func.sum(model.total_weight).label("total_weight")))
        filters = StatisticFilterUtils.filter(
            class_name=Orders,
            query=query,
            start_date=start_date,
            end_date=end_date,
            direction_id=direction_ids,
            transportation_type=transportation_type)
        data = await db.execute(filters)
        total_weight = data.scalar()
        return TotalWeightSchema(total_weight=total_weight if total_weight else 0.0)

    async def total_volume(self, db: AsyncSession = Depends(get_db), start_date: date = Query(None),
                           end_date: date = Query(None), direction_ids: List[int] = Query(None), transportation_type: TransportationType = Query(None)) -> TotalVolume:
        model = Orders
        query = (select(func.sum(model.total_volume).label("total_volume")))
        filters = StatisticFilterUtils.filter(
            class_name=Orders,
            query=query,
            start_date=start_date,
            end_date=end_date,
            direction_id=direction_ids,
            transportation_type=transportation_type)
        data = await db.execute(filters)
        total_volume = data.scalar()
        return TotalVolume(total_volume=total_volume if total_volume else 0.0)

    async def total_orders_count(self, db: AsyncSession = Depends(get_db), start_date: date = Query(None),
                                 end_date: date = Query(None),
                                 direction_ids: List[int] = Query(None), transportation_type: TransportationType = Query(None)) -> TotalOrdersCount:
        model = Orders
        query = (select(func.count(model.id).label("total_orders_count")))
        filters = StatisticFilterUtils.filter(
            class_name=Orders,
            query=query,
            start_date=start_date,
            end_date=end_date,
            direction_id=direction_ids,
            transportation_type=transportation_type)
        data = await db.execute(filters)
        total_orders_count = data.scalar()
        return TotalOrdersCount(total_orders_count=total_orders_count if total_orders_count else 0)

    async def orders(self, start_date: date = Query(None), end_date: date = Query(None),
                     direction_ids: List[int] = Query(None), db: AsyncSession = Depends(get_db), transportation_type: TransportationType = Query(None)) -> List[
        OrdersStatistics]:
        model = Orders
        query = (select(model.order_status, func.count(model.id).label("count")))
        filters = StatisticFilterUtils.filter(
            class_name=Orders,
            query=query,
            start_date=start_date,
            end_date=end_date,
            direction_id=direction_ids,
            transportation_type=transportation_type).group_by(
            model.order_status)
        data = await db.execute(filters)
        select_type = data.fetchall()
        result = []
        count_pending = 0
        for status, count in select_type:
            if status in ORDER_GROUPS["PENDING"]:
                count_pending += count
            elif status in ORDER_GROUPS["DELIVERED"]:
                result.append(OrdersStatistics(status=status, count=count))
            elif status in ORDER_GROUPS["CANCELLED"]:
                result.append(OrdersStatistics(status=status, count=count))
        result.append(OrdersStatistics(status="PENDING", count=count_pending))
        return result

    async def shippings(self, start_date: date = Query(None), end_date: date = Query(None), direction_ids: List[int] = Query(None), db: AsyncSession = Depends(get_db)) -> List[ShippingStatistics]:
        model = Shipping
        query = (select(model.shipping_type, func.count(
            model.id).label("count"), model.created_at))
        filters = StatisticFilterUtils.filter(
            class_name=Shipping,
            query=query,
            start_date=start_date,
            end_date=end_date,
            direction_id=direction_ids).group_by(
            model.shipping_type,
            model.created_at)
        data = await db.execute(filters)
        select_type = data.fetchall()
        result_dict = defaultdict(lambda: defaultdict(int))
        for shipping_type, count, created_at in select_type:
            result_dict[created_at.date()][shipping_type] += count
        result = [
            ShippingStatistics(
                shipping_types=[
                    ShippingTypeCount(
                        shipping_type=type,
                        count=count) for type,
                    count in counts.items()],
                created_at=date) for date,
            counts in result_dict.items()]
        result.sort(key=lambda x: x.created_at)
        return result

    async def payments(self, start_date: date = Query(None), end_date: date = Query(None), direction_ids: List[int] = Query(None), db: AsyncSession = Depends(get_db)) -> List[PaymentStatistics]:
        query = select(
            Payment.payment_type,
            func.count(Payment.id).label("count")
        ).join(
            Orders.payment
        )
        if start_date:
            query = query.filter(Orders.created_at >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            query = query.filter(Orders.created_at <= datetime.combine(end_date, datetime.max.time()))
        if direction_ids:
            query = query.filter(Orders.direction_id.in_(direction_ids))
        query = query.group_by(Payment.payment_type)
        data = await db.execute(query)
        select_type = data.fetchall()
        result = []
        for status, count in select_type:
            if status == PaymentType.CASH.value:
                result.append(PaymentStatistics(
                    payment_type=status, count=count))
            elif status == PaymentType.ONLINE.value:
                result.append(PaymentStatistics(
                    payment_type=status, count=count))
        return result

    async def couriers(self, start_date: date = Query(None), end_date: date = Query(None), direction_ids: List[int] = Query(None)) -> List[PaymentStatistics]:
        pass

    async def get_courier_statistics(self, start_date: date = Query(None), end_date: date = Query(None),
                                     direction_ids: List[int] = Query(None),
                                     transportation_type: list[TransportationType] = Query(None),
                                     db: AsyncSession = Depends(get_db)) -> list[CourierStatisticsSchema]:
        selected_filter = or_(
            UsersOrders.status == OrderStatus.COURIER_DELIVERING_TO_WAREHOUSE.value,
            UsersOrders.status == OrderStatus.ACCEPTED_TO_WAREHOUSE.value
        )
        delivered_filter = UsersOrders.status == OrderStatus.DELIVERED.value

        if direction_ids:
            direction_filter = Orders.direction_id.in_(direction_ids)
            selected_filter = and_(selected_filter, direction_filter)
            delivered_filter = and_(delivered_filter, direction_filter)

        if transportation_type:
            transportation_values = [t.value for t in transportation_type]
            selected_filter = and_(selected_filter, Directions.transportation_type.in_(transportation_values))
            delivered_filter = and_(delivered_filter, Directions.transportation_type.in_(transportation_values))

        if start_date:
            date_range = Orders.created_at >= datetime.combine(start_date, datetime.min.time())
            selected_filter = and_(selected_filter, date_range)
            delivered_filter = and_(delivered_filter, date_range)
        if end_date:
            date_range = Orders.created_at <= datetime.combine(end_date, datetime.max.time())
            selected_filter = and_(selected_filter, date_range)
            delivered_filter = and_(delivered_filter, date_range)

        query = select(
            Users.id.label('user_id'),
            Users.first_name,
            Users.last_name,
            func.count(case((selected_filter, UsersOrders.order_id), else_=None)).label('selected_orders'),
            func.count(case((delivered_filter, UsersOrders.order_id), else_=None)).label('delivered_orders'),
            func.sum(case((delivered_filter, Payment.amount), else_=0)).label('total_profit')
        ).outerjoin(UsersOrders, Users.id == UsersOrders.user_id
                    ).outerjoin(Orders, Orders.id == UsersOrders.order_id
                                ).outerjoin(Directions, Orders.direction_id == Directions.id
                                            ).outerjoin(Payment, Orders.id == Payment.order_id
                                                        ).group_by(
            Users.id, Users.first_name, Users.last_name
        )

        result = await db.execute(query)
        result = result.all()
        return [
            CourierStatisticsSchema(
                user_id=row[0],
                courier_name=f"{row[1]} {row[2]}",
                selected_orders=row[3],
                delivered_orders=row[4],
                total_profit=float(row[5]) if row[5] else 0.0
            )
            for row in result
        ]


statistic_service = StatisticService()
