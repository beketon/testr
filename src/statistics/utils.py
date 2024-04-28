from datetime import date, datetime
from typing import Dict, Generic, TypeVar

from src.directions.models import TransportationType, Directions

T = TypeVar("T")

from src.orders.models import Orders


class StatisticFilterUtils:

    @classmethod
    def filter(cls, class_name: Generic[T], query, direction_id: list[int] = None, start_date: date = None,
               end_date: date = None, transportation_type: TransportationType = None) -> list[Orders]:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        if direction_id is not None:
            query = query.where(class_name.direction_id.in_(direction_id))
        if start_date is not None:
            query = query.where(class_name.created_at >= start_datetime)
        if end_date is not None:
            query = query.where(class_name.created_at <= end_datetime)
        if transportation_type is not None:
            query = query.join(Directions, class_name.direction_id == Directions.id).where(Directions.transportation_type == transportation_type)
        return query
    
