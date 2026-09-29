import datetime

import pandas as pd
import streamlit as st

from menu import menu_with_redirect
from utils.db.games import Game, game_column_config_mapping, get_games_repo
from utils.db.players import get_players_repo
from utils.db.users import UserRole
from utils.pages import ToastNotifications, execute_with_toast, set_page
from utils.seasons import merge_seasons, st_seasons
from utils.streamlit.crud import CrudSpec, render_add_form, render_delete_form, render_edit_form

PAGE_NAME = "Zarządzanie gierkami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN])
ToastNotifications.render()

season = merge_seasons(st_seasons())

games_repo = get_games_repo()
players_repo = get_players_repo()

games = sorted(
    games_repo.find_by(season.get_datetime_query()), key=lambda g: g.datetime, reverse=True
)
players = sorted(players_repo.find_by({}), key=lambda p: p.surname)


def _render_game_players(_name, key, field, value):
    # Map stored player IDs to player objects for the multiselect widget.
    selected_players = [player for player in players if str(player.id) in (value or [])]
    return st.multiselect(
        field.title or "Zawodnicy",
        options=players,
        default=selected_players,
        key=key,
        help=field.description,
        format_func=lambda player: player.fullname,
    )


games_crud = CrudSpec(
    model=Game,
    objects=games,
    save=games_repo.save,
    delete=games_repo.delete,
    format_func=lambda game: game.date,
    add_values={
        "datetime": datetime.datetime.now(tz=datetime.UTC).replace(
            hour=12, minute=0, second=0, microsecond=0
        ),
        "cost": 150,
        "cost_per_player": 15,
    },
    field_renderers={"players_ids": _render_game_players},
)


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


new_game = render_add_form(
    games_crud,
    key="game_add",
    title="Dodaj gierkę",
)
if new_game:
    with execute_with_toast(f"Gierka '{new_game.date}' dodana!"):
        games_repo.save(new_game)
    st.rerun()


edited_game = render_edit_form(
    games_crud,
    key="game_edit",
    title="Edytuj gierkę",
    select_label="Wybierz gierkę",
)
if edited_game:
    with execute_with_toast(f"Gierka '{edited_game.date}' zedytowana!"):
        games_repo.save(edited_game)
    st.rerun()


deleted_games = render_delete_form(
    games_crud,
    key="game_delete",
    title="Usuń gierkę",
    select_label="Wybierz gierkę/gierki",
)
if deleted_games:
    for game_to_delete in deleted_games:
        with execute_with_toast(f"Gierka '{game_to_delete.date}' usunięta!"):
            games_repo.delete(game_to_delete)
    st.rerun()
