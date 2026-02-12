import streamlit as st

from menu import menu_with_redirect
from utils.db.games import Game, Season, get_all_games

# is_player_in_game
from utils.db.players import get_all_players
from utils.pages import set_page

PAGE_NAME = "Hala 2025/2026"
set_page(PAGE_NAME)

menu_with_redirect()

games = get_all_games(season=Season.INDOOR_25_26)
players = get_all_players()

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
                # "Zapłacono?": "✅" if is_game_paid_by_player(game, p) else "❌",
                "Zapłacono?": True,
            }
            for p in players_in_game
        ]
        st.dataframe(players_to_show)
