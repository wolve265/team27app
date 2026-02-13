import datetime as dt
from enum import StrEnum
from typing import Self

import streamlit as st
from pydantic import BaseModel, computed_field
from pydantic_mongo import AbstractRepository, PydanticObjectId

from utils.db.client import get_client, get_db

client = get_client()

game_column_config_mapping = {
    "id": None,
    "datetime": st.column_config.DateColumn("Data", format="DD.MM.YYYY"),
    "season": None,
    "cost": st.column_config.NumberColumn("Koszt", format="%d zł"),
    "players_ids": None,
    "players_count": "Liczba graczy",
}


class Season(StrEnum):
    INDOOR_25_26 = "indoor_25_26"

    @classmethod
    def list_all(cls) -> list[Self]:
        return [e for e in cls]


class Game(BaseModel):
    id: PydanticObjectId | None = None
    datetime: dt.datetime
    season: Season
    cost: int
    players_ids: list[str]

    @computed_field(repr=False)
    @property
    def date(self) -> str:
        return self.datetime.strftime("%d.%m.%Y")

    @computed_field(repr=False)
    @property
    def players_count(self) -> int:
        return len(self.players_ids)


class GamesRepository(AbstractRepository[Game]):
    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        collection_name = "games"


def get_games_repo() -> GamesRepository:
    return GamesRepository(get_db())


def get_all_games(season: Season | None = None) -> list[Game]:
    """Pull all games from the collection.

    Args:
        season: name of the season to get all games. If None - get games from all seasons

    Returns:
        list of games
    """
    repo = GamesRepository(client["t27app"])
    season_filter = {"season": season} if season else {}
    games = repo.find_by(season_filter)
    items_l = sorted(games, key=lambda g: g.datetime, reverse=True)
    return items_l


def add_game(new_game: Game) -> None:
    """Add a game to the collection."""
    repo = GamesRepository(client["t27app"])
    games = repo.find_by({})
    if any(new_game.datetime == g.datetime for g in games):
        raise RuntimeError(f"Game '{new_game.datetime} already exists.")
    repo.save(new_game)


def edit_game(game: Game) -> None:
    """Update a game in the collection."""
    repo = GamesRepository(client["t27app"])
    repo.save(game)


def delete_game(game: Game) -> None:
    """Delete a game from the collection."""
    repo = GamesRepository(client["t27app"])
    repo.delete(game)


# def is_player_in_game(game: Game, game_player: GamePlayer) -> bool:
#     for gp in game.players_ids:
#         if gp.name == game_player.name and gp.surname == game_player.surname:
#             return True
#     return False
