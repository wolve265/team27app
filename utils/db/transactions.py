from pydantic import BaseModel
from pydantic_mongo import AbstractRepository, PydanticObjectId

from utils.db.client import get_db


class Transaction(BaseModel):
    id: PydanticObjectId | None = None
    name: str
    value: int


class TransactionsRepository(AbstractRepository[Transaction]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        collection_name = "transactions"


def get_transactions_repo() -> TransactionsRepository:
    return TransactionsRepository(get_db())
