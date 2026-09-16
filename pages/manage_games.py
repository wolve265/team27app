import datetime

import pandas as pd
import streamlit as st

from menu import menu_with_redirect
from utils.db.games import Game, game_column_config_mapping, get_games_repo
from utils.db.players import get_players_repo
from utils.db.users import UserRole
from utils.pages import ToastNotifications, execute_with_toast, set_page

PAGE_NAME = "Zarządzanie gierkami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])
ToastNotifications.render()


games_repo = get_games_repo()
players_repo = get_players_repo()

games = sorted(games_repo.find_by({}), key=lambda g: g.datetime, reverse=True)
players = sorted(players_repo.find_by({}), key=lambda p: p.surname)


with st.expander("Gierki", expanded=True):
    st.button("Odśwież")
    dumped_games = [g.model_dump() for g in games]
    games_df = pd.DataFrame(dumped_games)
    if not games_df.empty:
        games_df = games_df.sort_values(by="datetime", ascending=False)
        games_df = games_df.drop(columns="id")
        st.dataframe(
            data=games_df,
            hide_index=True,
            column_order=["datetime", "cost", "cost_per_player", "players_count"],
            column_config=game_column_config_mapping,
        )


with st.form("add_game_form"):
    st.subheader("Dodaj gierkę", text_alignment="center")
    date = st.date_input("Data", format="DD.MM.YYYY")
    dt = datetime.datetime.combine(date, datetime.time(hour=12), tzinfo=datetime.UTC)
    cost = st.number_input("Koszt gierki (zł)", value=150, min_value=0, max_value=None)
    cost_per_player = st.number_input("Koszt za gracza (zł)", value=15, min_value=0, max_value=None)
    add_players = st.multiselect(
        "Wybierz zawodników",
        options=players,
        format_func=lambda p: p.fullname,
    )
    submit = st.form_submit_button("Dodaj")
    if submit:
        game = Game(
            datetime=dt,
            cost=cost,
            cost_per_player=cost_per_player,
            players_ids=[str(p.id) for p in add_players],
        )
        with execute_with_toast(f"Gierka '{game.date}' dodana!"):
            games_repo.save(game)
        st.rerun()


def update_edit_game_form() -> None:
    if "edit_game" not in st.session_state:
        return
    if not st.session_state.edit_game:
        return
    game: Game = st.session_state.edit_game
    st.session_state.edit_date = game.datetime
    st.session_state.edit_cost = game.cost
    st.session_state.edit_cost_per_player = game.cost_per_player
    st.session_state.edit_players = [p for p in players if str(p.id) in game.players_ids]


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
        date = st.date_input("Data", key="edit_date", format="DD.MM.YYYY")
        dt = datetime.datetime.combine(date, datetime.time(hour=12), tzinfo=datetime.UTC)
        game_to_edit.datetime = dt
        game_to_edit.cost = st.number_input(
            "Koszt gierki (zł)", key="edit_cost", min_value=0, max_value=None
        )
        game_to_edit.cost_per_player = st.number_input(
            "Koszt za gracza (zł)",
            key="edit_cost_per_player",
            min_value=0,
            max_value=None,
        )
        edit_players = st.multiselect(
            "Wybierz zawodników",
            options=players,
            default=st.session_state.edit_players,
            format_func=lambda p: p.fullname,
        )
        game_to_edit.players_ids = [str(p.id) for p in edit_players]
        submit = st.button("Zapisz")
        if submit:
            with execute_with_toast(f"Gierka '{game_to_edit.date}' zedytowana!"):
                games_repo.save(game_to_edit)
            st.rerun()


with st.container(border=True):
    st.subheader("Usuń gierkę", text_alignment="center")
    games_to_delete = st.multiselect(
        "Wybierz gierkę/gierki",
        options=games,
        format_func=lambda g: g.date,
        key="delete_game",
    )
    if games_to_delete:
        submit = st.button("Usuń")
        if submit:
            for game_to_delete in games_to_delete:
                with execute_with_toast(f"Gierka '{game_to_delete.date}' usunięta!"):
                    games_repo.delete(game_to_delete)
            st.rerun()
