from typing import TypedDict

import streamlit as st
from pymongo.collection import Collection

from utils.db.client import get_client

client = get_client()

player_column_config_mapping = {
    "_id": None,
    "name": "Imię",
    "surname": "Nazwisko",
    "team27_number": st.column_config.NumberColumn(label="Numer"),
    "psid": None,
    "user_email": None,
}

class Player(TypedDict):
    name: str
    surname: str
    team27_number: int
    psid: str
    user_email: str


def is_player_linked_to_user(player: Player) -> bool:
    """Check if the player is linked to a user."""
    return bool(player["user_email"])


def is_player_linked_to_messenger(player: Player) -> bool:
    """Check if the player is linked to a messenger notification system."""
    return bool(player["psid"])


def is_player_team27_member(player: Player) -> bool:
    """Check if the player is a member of team 27."""
    return player["team27_number"] > 0


def get_all_players() -> list[Player]:
    """Pull all players from the collection."""
    collection: Collection[Player] = client.t27app.players
    players = collection.find()
    items_l = sorted(players, key=lambda p: p["surname"])
    return items_l


def add_player(player: Player) -> None:
    """Add a player to the collection."""
    collection: Collection[Player] = client.t27app.players
    players = collection.find()
    if any(all(player[key] == p[key] for key in ("name", "surname")) for p in players):
        raise RuntimeError(f"Player '{player['name']} {player['surname']}' already exists.")
    collection.insert_one(player)


def edit_player(player: Player) -> None:
    """Update a player in the collection."""
    collection: Collection[Player] = client.t27app.players
    collection.update_one(
        {"name": player["name"], "surname": player["surname"]},
        {"$set": player},
        upsert=True,
    )


def delete_player(player: Player) -> None:
    """Delete a player from the collection."""
    collection: Collection[Player] = client.t27app.players
    collection.delete_one({"name": player["name"], "surname": player["surname"]})
