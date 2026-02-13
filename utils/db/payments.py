from pydantic import BaseModel
from pydantic_mongo import AbstractRepository, PydanticObjectId

from utils.db.client import get_db
from utils.db.players import Player


class Payment(BaseModel):
    id: PydanticObjectId | None = None
    player_id: str
    value: int


class PaymentsRepository(AbstractRepository[Payment]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        collection_name = "payments"


def get_payments_repo() -> PaymentsRepository:
    return PaymentsRepository(get_db())


def get_player_payments(payments: list[Payment], player: Player) -> list[Payment]:
    player_payments = [pay for pay in payments if str(player.id) == pay.player_id]
    return player_payments


def get_player_payments_sum(payments: list[Payment], player: Player) -> int:
    player_payments = get_player_payments(payments, player)
    return sum([pay.value for pay in player_payments])
