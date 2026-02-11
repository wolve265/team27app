import datetime

import streamlit as st

from menu import menu_with_redirect
from utils.db.games import Game, GamePlayer, Season, add_game, delete_game, edit_game, get_all_games
from utils.db.players import get_all_players
from utils.db.users import UserRole

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])

games = get_all_games()
players = get_all_players()

if "notification" in st.session_state:
    notification = st.session_state.pop("notification")
    icon = notification["icon"]
    st.toast(notification["msg"], icon=icon)

st.header("Zarządzanie gierkami")

with st.expander("Gierki", expanded=True):
    st.button("Odśwież")
    games_to_show = [
        {
            # "Sezon": g["season"],
            "Data": g.date,
            "Cena (zł)": g.cost,
            "Liczba graczy": len(g.players),
        }
        for g in sorted(games, key=lambda g: g.datetime, reverse=True)
    ]
    st.table(games_to_show)


with st.form("add_game_form"):
    st.subheader("Dodaj gierkę", text_alignment="center")
    season = st.selectbox("Wybierz sezon", options=Season.list_all())
    date = st.date_input("Data", format="DD.MM.YYYY")
    dt = datetime.datetime.combine(date, datetime.time(hour=12))
    cost = st.number_input("Koszt (zł)", min_value=0, max_value=None)
    add_players = st.multiselect(
        "Uczestnicy", options=players, format_func=lambda p: f"{p['name']} {p['surname']}"
    )
    submit = st.form_submit_button("Dodaj")
    if submit:
        game = Game(
            datetime=dt,
            season=Season(season),
            cost=cost,
            players=add_players,
        )
        try:
            add_game(game)
        except Exception as e:
            st.session_state.notification = {"msg": str(e), "icon": "❌"}
        else:
            st.session_state.notification = {
                "icon": "✅",
                "msg": f"Gierka '{game.date}' dodana!",
            }
        finally:
            st.rerun()


def update_edit_game_form() -> None:
    if "edit_game" not in st.session_state:
        return
    if not st.session_state.edit_game:
        return
    game: Game = st.session_state["edit_game"]
    st.session_state.edit_season = game.season
    st.session_state.edit_cost = game.cost
    st.session_state.edit_players = game.players


with st.container(border=True):
    st.subheader("Edytuj gierkę", text_alignment="center")
    game_to_edit = st.selectbox(
        "Wybierz gierkę",
        index=None,
        format_func=lambda g: g.date,
        key="edit_game",
        options=games,
        on_change=update_edit_game_form,
    )
    if game_to_edit:
        game_to_edit.season = st.selectbox(
            "Wybierz sezon",
            key="edit_season",
            options=Season.list_all(),
        )
        game_to_edit.cost = st.number_input(
            "Koszt (zł)",
            key="edit_cost",
            min_value=0,
            max_value=None,
        )
        game_to_edit.players = st.multiselect(
            "Uczestnicy",
            # key="edit_players",
            options=[GamePlayer(**p) for p in players],
            default=st.session_state.edit_players,
            format_func=lambda gp: f"{gp.name} {gp.surname}",
        )
        submit = st.button("Zapisz")
        if submit:
            try:
                edit_game(game_to_edit)
            except Exception as e:
                st.session_state.notification = {"msg": str(e), "icon": "❌"}
            else:
                st.session_state.notification = {
                    "icon": "✅",
                    "msg": f"Gierka '{game_to_edit.date}' zedytowana!",
                }
            finally:
                st.rerun()


with st.container(border=True):
    st.subheader("Usuń gierkę", text_alignment="center")
    game_to_delete = st.selectbox(
        "Wybierz gierkę",
        index=None,
        format_func=lambda g: g.date,
        key="delete_game",
        options=games,
    )
    if game_to_delete:
        submit = st.button("Usuń")
        if submit:
            try:
                delete_game(game_to_delete)
            except Exception as e:
                st.session_state.notification = {"msg": str(e), "icon": "❌"}
            else:
                st.session_state.notification = {
                    "icon": "✅",
                    "msg": f"Gierka '{game_to_delete.date}' usunięta!",
                }
            finally:
                st.rerun()
