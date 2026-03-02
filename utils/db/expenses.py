from pydantic import BaseModel
from pydantic_mongo import AbstractRepository, PydanticObjectId

from utils.db.client import get_db


class Expense(BaseModel):
    id: PydanticObjectId | None = None
    name: str
    value: int


class ExpensesRepository(AbstractRepository[Expense]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        collection_name = "expenses"


def get_expenses_repo() -> ExpensesRepository:
    return ExpensesRepository(get_db())
