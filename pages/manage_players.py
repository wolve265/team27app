import pandas as pd
import streamlit as st

from menu import menu_with_redirect
from utils.db.players import (
    Player,
    get_players_repo,
    player_column_config_mapping,
)
from utils.db.users import UserRole
from utils.pages import ToastNotifications, execute_with_toast, set_page
from utils.streamlit.crud import CrudSpec, render_add_form, render_delete_form, render_edit_form

PAGE_NAME = "Zarządzanie zawodnikami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN])
ToastNotifications.render()


players_repo = get_players_repo()

players = sorted(players_repo.find_by({}), key=lambda p: p.surname)
players_crud = CrudSpec(
    model=Player,
    objects=players,
    save=players_repo.save,
    delete=players_repo.delete,
)


with st.expander("Zawodnicy", expanded=True):
    t27_only = st.checkbox("Tylko Team27")
    cols = st.columns(3)
    cols[0].write("Liczba zawodników:")
    cols[1].write(f"Team27 - {len([p for p in players if p.team27_number > 0])}")
    cols[2].write(f"Ogółem - {len(players)}")
    dumped_players = [p.model_dump() for p in players if not (t27_only and p.team27_number <= 0)]
    players_df = pd.DataFrame(dumped_players)
    if not players_df.empty:
        players_df = players_df.drop(columns="id")
        styled_df = players_df.style.apply(
            lambda x: ["color: cyan" if val > 0 else "" for val in x], subset=["team27_number"]
        )
        st.dataframe(
            data=styled_df,
            hide_index=True,
            column_order=["team27_number", "name", "surname"],
            column_config=player_column_config_mapping,
        )


new_player = render_add_form(
    players_crud,
    key="player_add",
    title="Dodaj zawodnika",
)
if new_player:
    with execute_with_toast(f"Zawodnik '{new_player.fullname}' dodany!"):
        players_repo.save(new_player)
    st.rerun()


edited_player = render_edit_form(
    players_crud,
    key="player_edit",
    title="Edytuj zawodnika",
    select_label="Wybierz zawodnika",
)
if edited_player:
    with execute_with_toast(f"Zawodnik '{edited_player.fullname}' zedytowany!"):
        players_repo.save(edited_player)
    st.rerun()


deleted_players = render_delete_form(
    players_crud,
    key="player_delete",
    title="Usuń zawodnika",
    select_label="Wybierz zawodnika/zawodników",
)
if deleted_players:
    for player_to_delete in deleted_players:
        with execute_with_toast(f"Zawodnik '{player_to_delete.fullname}' usunięty!"):
            players_repo.delete(player_to_delete)
    st.rerun()
