from src.warehouse.constants import ErrorCode
from src.exceptions import NotFound

class WarehouseNotFound(NotFound):
    DETAIL = ErrorCode.WAREHOUSE_NOT_FOUND
