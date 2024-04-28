from src.geography.constants import ErrorCode
from src.exceptions import NotFound

class JsonNotFound(NotFound):
    DETAIL = ErrorCode.JSON_NOT_FOUND