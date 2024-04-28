from src.expenses.constants import ErrorCode
from src.exceptions import BadRequest, NotFound

class ExpenseNotUnique(BadRequest):
    DETAIL = ErrorCode.EXPENSE_NOT_UNIQUE

class ExpenseNotFound(NotFound):
    DETAIL = ErrorCode.EXPENSE_NOT_FOUND