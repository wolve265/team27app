from typing import TypedDict

from pymongo.collection import Collection

from utils.db.client import get_client

client = get_client()

class Player(TypedDict):
    number: int
    name: str
    surname: str
    psid: str


def get_all_players() -> list[Player]:
    """Pull all players from the collection."""
    collection: Collection[Player] = client.t27app.players
    players = collection.find()
    items_l = list(players)
    return items_l
