import datetime as dt

from pydantic import BaseModel, computed_field
from pydantic_mongo import AbstractRepository, PydanticObjectId

from utils.db.client import get_db
from utils.db.players import Player
from utils.db.seasons import Season, Seasons


class Payment(BaseModel):
    id: PydanticObjectId | None = None
    datetime: dt.datetime
    player_id: str
    value: int

    @computed_field(repr=False)
    @property
    def date(self) -> str:
        return self.datetime.strftime("%d.%m.%Y")

    @computed_field(repr=False)
    @property
    def season(self) -> Season:
        return Seasons.from_datetime(self.datetime)

    def format(self, players: list[Player]) -> str:
        player = next(p for p in players if str(p.id) == self.player_id)
        return f"{player.fullname} - {self.value} zł"


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
