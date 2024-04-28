from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, String

from src.common.models import TimestampMixin
from src.database import Base


# TODO: use src.orders.models.OrderStatus instead of this enum
class ActionCode(Enum):
    CREATED = "ORDER_CREATED"
    MANAGER_APPROVED = "MANAGER_APPROVED"
    ACCEPTED_TO_WAREHOUSE = "ACCEPTED_TO_WAREHOUSE"
    COURIER_DELIVERING_TO_WAREHOUSE = "COURIER_DELIVERING_TO_WAREHOUSE"
    ARRIVED_MIDDLE_WAREHOUSE = "ARRIVED_MIDDLE_WAREHOUSE"
    IN_TRANSIT = "IN_TRANSIT"
    PARTIALLY_IN_TRANSIT = "PARTIALLY_IN_TRANSIT"
    DELIVERING_TO_RECIPIENT = "DELIVERING_TO_RECIPIENT"
    ARRIVED_TO_DESTINATION = "ARRIVED_TO_DESTINATION"
    DELIVERED = "DELIVERED"
    NOT_DELIVERED = "NOT_DELIVERED"


ACTION_CODE_TO_ACTION_DESCRIPTION = {
    ActionCode.CREATED: "Создан заказ",
    ActionCode.MANAGER_APPROVED: "Менеджер %s подтвердил товар",
    ActionCode.COURIER_DELIVERING_TO_WAREHOUSE: "Курьер %s забрал товар",
    ActionCode.IN_TRANSIT: "В пути",
    ActionCode.PARTIALLY_IN_TRANSIT: "Частичное отправление",
    ActionCode.ACCEPTED_TO_WAREHOUSE: "Товар находится на складе %s города %s - %s",
    ActionCode.DELIVERING_TO_RECIPIENT: "Товар доставляется получателю - %s",
    ActionCode.ARRIVED_TO_DESTINATION: "Товар прибыл на склад %s города %s - %s",
    ActionCode.DELIVERED: "Товар доставлен получателю - %s",
    ActionCode.NOT_DELIVERED: "Товар не доставлен получателю",
    ActionCode.ARRIVED_MIDDLE_WAREHOUSE: " %s прибыл в промежуточный склад"
}


class ActionHistory(Base, TimestampMixin):
    __tablename__ = "action_history"

    id = Column(Integer, primary_key=True, index=True)
    order_item_id = Column(Integer, ForeignKey(
        "order_items.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    previous_action = Column(Integer, ForeignKey("action_history.id"))
    action_description = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("users.id"))
    manager_id = Column(Integer, ForeignKey("users.id"))
    courier_id = Column(Integer, ForeignKey("users.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    warehouse_manager_id = Column(Integer, ForeignKey("users.id"))
    arrival_city_id = Column(Integer, ForeignKey("cities.id"))
    departure_city_id = Column(Integer, ForeignKey("cities.id"))
    action_code = Column(String, nullable=False)
