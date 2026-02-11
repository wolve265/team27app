import streamlit as st

from menu import menu_with_redirect
from utils.db.games import Game, GamePlayer, Season, get_all_games, is_player_in_game
from utils.db.players import get_all_players

menu_with_redirect()

games = get_all_games(season=Season.INDOOR_25_26)
players = get_all_players()

st.header("Hala 2025/2026")
st.button("Odśwież")


# prototype to be moved
def is_game_paid_by_player(game: Game, game_player: GamePlayer) -> bool:
    player_in_game = is_player_in_game(game, game_player)
    if not player_in_game:
        return True
    # TODO:
    return False


for game in sorted(games, key=lambda g: g.datetime, reverse=True):
    with st.expander(game.date, expanded=True):
        st.subheader(game.date)
        players_to_show = [
            {
                "Imię": gp.name,
                "Nazwisko": gp.surname,
                "Zapłacono?": "✅" if is_game_paid_by_player(game, gp) else "❌",
            }
            for gp in game.players
        ]
        st.table(players_to_show)
