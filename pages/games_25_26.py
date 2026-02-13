import streamlit as st

from menu import menu_with_redirect
from utils.db.games import Season, get_games_repo, get_player_games, get_player_games_cost
from utils.db.payments import get_payments_repo, get_player_payments_sum
from utils.db.players import get_all_players
from utils.pages import set_page

PAGE_NAME = "Hala 2025/2026"
set_page(PAGE_NAME)

menu_with_redirect()

games_repo = get_games_repo()
payments_repo = get_payments_repo()

games = sorted(
    games_repo.find_by({"season": Season.INDOOR_25_26}), key=lambda g: g.datetime, reverse=True
)
players = get_all_players()
payments = list(payments_repo.find_by({}))

st.button("Odśwież")


# # prototype to be moved
# def is_game_paid_by_player(game: Game, game_player: GamePlayer) -> bool:
#     player_in_game = is_player_in_game(game, game_player)
#     if not player_in_game:
#         return True
#     # TODO:
#     return False


for i, game in enumerate(games):
    expanded = i == 0
    games_since_this_one = [g for g in games if g.datetime <= game.datetime]
    with st.expander(game.date, expanded=expanded):
        st.subheader(game.date, text_alignment="center")
        players_in_game = [p for p in players if str(p.id) in game.players_ids]
        left, mid, right = st.columns(3)
        left.write("Liczba zawodników:")
        mid.write(f"Team27 - {len([p for p in players_in_game if p.team27_number])}")
        right.write(f"Ogółem - {len(players_in_game)}")
        players_to_show = [
            {
                "Imię": p.name,
                "Nazwisko": p.surname,
                "Zapłacono?": (pay_sum:=get_player_payments_sum(payments, p)) >= (game_cost:=get_player_games_cost(games_since_this_one, p)),
                "Liczba gierek": len(get_player_games(games_since_this_one, p)),
                "Suma wpłat": pay_sum,
                "Koszt gierek": game_cost,
                "Bilans": pay_sum - game_cost,
            }
            for p in players_in_game
        ]
        st.dataframe(players_to_show)
