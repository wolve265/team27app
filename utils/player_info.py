from dataclasses import dataclass
from typing import Self

from utils.db.games import Game, get_player_games, get_player_games_cost
from utils.db.payments import Payment, get_player_payments_sum
from utils.db.players import Player


@dataclass
class PlayerInfo:
    player: Player
    player_games: list[Game]
    payments_sum: int
    games_cost: int
    balance: int
    game_paid: bool
    game_count: int

    @classmethod
    def from_player(cls, player: Player, games: list[Game], payments: list[Payment]) -> Self:
        payments_sum = get_player_payments_sum(payments, player)
        games_cost = get_player_games_cost(games, player)
        player_games = get_player_games(games, player)
        return cls(
            player=player,
            player_games=player_games,
            payments_sum=payments_sum,
            games_cost=games_cost,
            balance=payments_sum - games_cost,
            game_paid=payments_sum >= games_cost,
            game_count=len(player_games),
        )
