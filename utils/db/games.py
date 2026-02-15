import datetime as dt
from enum import StrEnum
from typing import Self

import streamlit as st
from pydantic import BaseModel, computed_field
from pydantic_mongo import AbstractRepository, PydanticObjectId

from utils.db.client import get_db
from utils.db.players import Player

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
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        collection_name = "games"


def get_games_repo() -> GamesRepository:
    return GamesRepository(get_db())


def get_player_games(games: list[Game], player: Player) -> list[Game]:
    player_games = [g for g in games if str(player.id) in g.players_ids]
    return player_games


def get_player_games_cost(games: list[Game], player: Player) -> int:
    player_games = get_player_games(games, player)
    games_cost = sum([g.cost for g in player_games])
    return games_cost
