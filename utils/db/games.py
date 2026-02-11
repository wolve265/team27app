import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel
from pydantic_mongo import AbstractRepository, PydanticObjectId

from utils.db.client import get_client


class Season(StrEnum):
    INDOOR_25_26 = "indoor_25_26"

    @classmethod
    def list_all(cls) -> list[Self]:
        return [e for e in cls]


class GamePlayer(BaseModel):
    name: str
    surname: str


class Game(BaseModel):
    id: PydanticObjectId | None = None
    datetime: datetime.datetime
    season: Season
    cost: int
    players: list[GamePlayer]

    @property
    def date(self) -> str:
        return self.datetime.strftime("%d.%m.%Y")


class GamesRepository(AbstractRepository[Game]):
    class Meta:
        collection_name = "games"


client = get_client()


def get_all_games(season: Season | None = None) -> list[Game]:
    """Pull all games from the collection.

    Args:
        season: name of the season to get all games. If None - get games from all seasons

    Returns:
        list of games
    """
    games_repo = GamesRepository(client["t27app"])
    season_filter = {"season": season} if season else {}
    games = games_repo.find_by(season_filter)
    items_l = sorted(games, key=lambda g: g.datetime)
    return items_l


def add_game(game: Game) -> None:
    """Add a game to the collection."""
    games_repo = GamesRepository(client["t27app"])
    games = games_repo.find_by({})
    if any(game.datetime == g.datetime for g in games):
        raise RuntimeError(f"Game '{game.datetime} already exists.")
    games_repo.save(game)


def edit_game(game: Game) -> None:
    """Update a game in the collection."""
    games_repo = GamesRepository(client["t27app"])
    games_repo.save(game)


def delete_game(game: Game) -> None:
    """Delete a game from the collection."""
    games_repo = GamesRepository(client["t27app"])
    games_repo.delete(game)


def is_player_in_game(game: Game, game_player: GamePlayer) -> bool:
    for gp in game.players:
        if gp.name == game_player.name and gp.surname == game_player.surname:
            return True
    return False
