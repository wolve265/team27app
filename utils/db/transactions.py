import datetime as dt

from pydantic import BaseModel, Field, computed_field
from pydantic_mongo import AbstractRepository, PydanticObjectId

from utils.db.client import get_db


class Transaction(BaseModel):
    id: PydanticObjectId | None = None
    datetime: dt.datetime = Field(title="Data")
    name: str = Field(title="Nazwa transakcji")
    value: int = Field(title="Kwota (zł)")

    def __str__(self) -> str:
        return f"{self.date} | {self.name} - {self.value} zł"

    @computed_field(repr=False)
    @property
    def date(self) -> str:
        return self.datetime.strftime("%d.%m.%Y")

    def is_expense(self) -> bool:
        return self.value < 0

    def is_revenue(self) -> bool:
        return self.value >= 0


class TransactionsRepository(AbstractRepository[Transaction]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        collection_name = "transactions"


def get_transactions_repo() -> TransactionsRepository:
    return TransactionsRepository(get_db())
