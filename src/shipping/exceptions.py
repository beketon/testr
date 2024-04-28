from src.shipping.constants import ErrorCode
from src.exceptions import NotFound

class ShippingNotFound(NotFound):
    DETAIL = ErrorCode.SHIPPING_NOT_FOUND

class ShippingRespondNotFound(NotFound):
    DETAIL = ErrorCode.SHIPPING_RESPOND_NOT_FOUND