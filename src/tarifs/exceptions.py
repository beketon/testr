from src.exceptions import NotFound
from src.tarifs.constants import ErrorCode


class TarifNotFound(NotFound):
    DETAIL = ErrorCode.TARIF_NOT_FOUND
