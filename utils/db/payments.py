from collections.abc import Iterable

from pydantic import BaseModel
from pydantic_mongo import AbstractRepository, PydanticObjectId

from utils.db.client import get_db
from utils.db.players import Player


class Payment(BaseModel):
    id: PydanticObjectId | None = None
    player_id: str
    value: int


class PaymentsRepository(AbstractRepository[Payment]):
    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        collection_name = "payments"

    def get_player_payments(
        self, player: Player, projection: dict[str, int] | None = None
    ) -> Iterable[Payment]:
        query = {"player_id": str(player.id)}
        player_payments = self.find_by(query, projection=projection)
        return player_payments

    def get_player_payments_sum(self, player: Player) -> int:
        pipeline = [
            {
                "$group": {
                    "total": {"$sum": "$value"},
                },
            },
        ]
        result = self.get_collection().aggregate(pipeline)
        return result["total"] if result else 0


def get_payments_repo() -> PaymentsRepository:
    return PaymentsRepository(get_db())
