from src.orders.constants import ErrorCode
from src.exceptions import NotFound

class OrderItemNotFound(NotFound):
    DETAIL = ErrorCode.ORDER_ITEM_NOT_FOUND