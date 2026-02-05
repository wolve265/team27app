from __future__ import annotations

from typing import Any

from pymongo import MongoClient

from lib.config import get_database_name, require_secret

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        uri = require_secret("MONGODB_URI")
        _client = MongoClient(uri, appname="streamlit-poc")
    return _client


def get_db():
    return get_client()[get_database_name()]


def get_collection(name: str):
    return get_db()[name]


def upsert_user(user: dict[str, Any]) -> None:
    users = get_collection("users")
    users.update_one({"email": user["email"]}, {"$set": user}, upsert=True)


def list_games(email: str) -> list[dict[str, Any]]:
    games = get_collection("games")
    return list(games.find({"email": email}).sort("created_at", -1))


def get_game(game_id: str, email: str) -> dict[str, Any] | None:
    games = get_collection("games")
    return games.find_one({"_id": game_id, "email": email})


def insert_game(game: dict[str, Any]) -> None:
    games = get_collection("games")
    games.insert_one(game)


def update_game(game_id: str, email: str, updates: dict[str, Any]) -> None:
    games = get_collection("games")
    games.update_one({"_id": game_id, "email": email}, {"$set": updates})


def delete_game(game_id: str, email: str) -> None:
    games = get_collection("games")
    games.delete_one({"_id": game_id, "email": email})


def list_payments(email: str) -> list[dict[str, Any]]:
    payments = get_collection("payments")
    return list(payments.find({"email": email}).sort("date", -1))


def insert_payment_event(event: dict[str, Any]) -> None:
    payments = get_collection("payment_events")
    payments.insert_one(event)
