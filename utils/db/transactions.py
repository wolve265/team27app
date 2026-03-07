from pydantic import BaseModel
from pydantic_mongo import AbstractRepository, PydanticObjectId

from utils.db.client import get_db


class Transaction(BaseModel):
    id: PydanticObjectId | None = None
    name: str
    value: int

    def is_expense(self) -> bool:
        return self.value < 0

    def is_revenue(self) -> bool:
        return self.value >= 0


class TransactionsRepository(AbstractRepository[Transaction]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        collection_name = "transactions"


def get_transactions_repo() -> TransactionsRepository:
    return TransactionsRepository(get_db())
