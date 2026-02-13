import datetime

import pandas as pd
import streamlit as st

from menu import menu_with_redirect
from utils.db.games import Game, Season, game_column_config_mapping, get_games_repo
from utils.db.players import get_all_players
from utils.db.users import UserRole
from utils.pages import set_page

PAGE_NAME = "Zarządzanie gierkami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])

games_repo = get_games_repo()

games = sorted(games_repo.find_by({}), key=lambda g: g.datetime, reverse=True)
players = get_all_players()

if "notification" in st.session_state:
    notification = st.session_state.pop("notification")
    icon = notification["icon"]
    st.toast(notification["msg"], icon=icon)


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
            column_order=["date", "cost", "players_count"],
            column_config=game_column_config_mapping,
        )


with st.form("add_game_form"):
    st.subheader("Dodaj gierkę", text_alignment="center")
    season = st.selectbox("Wybierz sezon", options=Season.list_all())
    date = st.date_input("Data", format="DD.MM.YYYY")
    dt = datetime.datetime.combine(date, datetime.time(hour=12))
    cost = st.number_input("Koszt (zł)", min_value=0, max_value=None)
    add_players = st.multiselect(
        "Uczestnicy",
        options=players,
        format_func=lambda p: p.fullname,
    )
    submit = st.form_submit_button("Dodaj")
    if submit:
        game = Game(
            datetime=dt,
            season=Season(season),
            cost=cost,
            players_ids=[str(p.id) for p in add_players],
        )
        try:
            games_repo.save(game)
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
        edit_players = st.multiselect(
            "Uczestnicy",
            # key="edit_players",
            options=players,
            default=st.session_state.edit_players,
            format_func=lambda p: p.fullname,
        )
        game_to_edit.players_ids = [str(p.id) for p in edit_players]
        submit = st.button("Zapisz")
        if submit:
            try:
                games_repo.save(game_to_edit)
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
                games_repo.delete(game_to_delete)
            except Exception as e:
                st.session_state.notification = {"msg": str(e), "icon": "❌"}
            else:
                st.session_state.notification = {
                    "icon": "✅",
                    "msg": f"Gierka '{game_to_delete.date}' usunięta!",
                }
            finally:
                st.rerun()
