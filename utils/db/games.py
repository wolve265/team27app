from enum import StrEnum
from typing import TypedDict

from pymongo.collection import Collection

from utils.db.client import get_client

client = get_client()


class Season(StrEnum):
    INDOOR_25_26 = "indoor_25_26"


class GamePlayer(TypedDict):
    name: str
    surname: str


class Game(TypedDict):
    date: str
    season: Season
    cost: int
    players: list[GamePlayer]


def get_all_games(season: Season | None) -> list[Game]:
    """Pull all games from the collection.

    Args:
        season: name of the season to get all games. If None - get games from all seasons

    Returns:
        list of games
    """
    collection: Collection[Game] = client.t27app.games
    season_filter = {"season": season} if season else {}
    games = collection.find(season_filter)
    items_l = sorted(games, key=lambda g: g["date"])
    return items_l


def add_game(game: Game) -> None:
    """Add a game to the collection."""
    collection: Collection[Game] = client.t27app.games
    games = collection.find()
    if any(game["date"] == g["date"] for g in games):
        raise RuntimeError(f"Game '{game['date']} already exists.")
    collection.insert_one(game)


def edit_game(game: Game) -> None:
    """Update a game in the collection."""
    collection: Collection[Game] = client.t27app.games
    collection.update_one({"date": game["date"]}, {"$set": game}, upsert=True)


def delete_game(game: Game) -> None:
    """Delete a game from the collection."""
    collection: Collection[Game] = client.t27app.games
    collection.delete_one({"date": game["date"]})


def is_player_in_game(game: Game, game_player: GamePlayer) -> bool:
    for gp in game["players"]:
        if gp["name"] == game_player["name"] and gp["surname"] == game_player["surname"]:
            return True
    return False
