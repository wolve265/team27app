from collections.abc import Callable
from typing import Any

from pydantic_mongo import AbstractRepository

from team27app.utils.db.games import Game, get_games_repo
from team27app.utils.db.payments import Payment, get_payments_repo
from team27app.utils.db.players import Player, get_players_repo
from team27app.utils.db.transactions import Transaction, get_transactions_repo
from team27app.utils.db.users import User, get_users_repo

REPO_MODEL_PAIRS: list[tuple[Any, Callable[..., AbstractRepository[Any]]]] = [
    (Game, get_games_repo),
    (Payment, get_payments_repo),
    (Player, get_players_repo),
    (Transaction, get_transactions_repo),
    (User, get_users_repo),
]


def test_all_db_documents_are_pydantic_instances() -> None:
    for model_class, repo_factory in REPO_MODEL_PAIRS:
        repo = repo_factory()
        documents = list(repo.find_by({}))
        assert all(isinstance(doc, model_class) for doc in documents)
