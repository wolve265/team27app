import pandas as pd
import streamlit as st

from menu import menu_with_redirect
from utils.db.players import (
    Player,
    add_player,
    delete_player,
    edit_player,
    get_all_players,
    player_column_config_mapping,
)
from utils.db.users import UserRole
from utils.pages import set_page

PAGE_NAME = "Zarządzanie zawodnikami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])

players = get_all_players()


if "notification" in st.session_state:
    notification = st.session_state.pop("notification")
    icon = notification["icon"]
    st.toast(notification["msg"], icon=icon)


with st.expander("Zawodnicy", expanded=True):
    st.button("Odśwież")
    t27_only = st.checkbox("Tylko Team27")
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
        left, mid, right = st.columns(3)
        left.write("Liczba zawodników:")
        mid.write(f"Team27 - {len(players_df.loc[players_df['team27_number'] > 0])}")
        right.write(f"Ogółem - {len(players_df)}")


with st.form("add_player_form"):
    st.subheader("Dodaj zawodnika", text_alignment="center")
    name = st.text_input("Imię")
    surname = st.text_input("Nazwisko")
    team27_number = st.number_input(
        "Numer w Team 27",
        key="add_team27_number",
        min_value=0,
        max_value=99,
        step=1,
        help="Wpisz 0, jeśli zawodnik nie jest członkiem Team 27.",
    )
    psid = st.text_input(
        "PSID",
        key="add_psid",
        help="Zostaw puste, jeśli zawodnik nie jest połączony z systemem powiadomień.",
    )
    user_email = st.text_input(
        "Email użytkownika",
        key="add_user_email",
        help="Zostaw puste, jeśli zawodnik nie jest połączony z żadnym użytkownikiem.",
    )
    submit = st.form_submit_button("Dodaj")
    if submit:
        if not name:
            st.error("Imię jest wymagane!")
        elif not surname:
            st.error("Nazwisko jest wymagane!")
        else:
            player = Player(
                name=name,
                surname=surname,
                team27_number=team27_number,
                psid=psid,
                user_email=user_email,
            )
            try:
                add_player(player)
            except Exception as e:
                st.session_state.notification = {"msg": str(e), "icon": "❌"}
            else:
                st.session_state.notification = {
                    "icon": "✅",
                    "msg": f"Zawodnik '{player.fullname}' dodany!",
                }
            finally:
                st.rerun()


def update_edit_player_form() -> None:
    if "edit_player" not in st.session_state:
        return
    if not st.session_state.edit_player:
        return
    player: Player = st.session_state["edit_player"]
    st.session_state.edit_team27_number = player.team27_number
    st.session_state.edit_psid = player.psid
    st.session_state.edit_user_email = player.user_email


with st.container(border=True):
    st.subheader("Edytuj zawodnika", text_alignment="center")
    player_to_edit = st.selectbox(
        "Wybierz zawodnika",
        index=None,
        format_func=lambda p: p.fullname,
        key="edit_player",
        options=players,
        on_change=update_edit_player_form,
    )
    if player_to_edit:
        player_to_edit.team27_number = st.number_input(
            "Numer w Team 27",
            key="edit_team27_number",
            min_value=0,
            max_value=99,
            step=1,
            help="Wpisz 0, jeśli zawodnik nie jest członkiem Team 27.",
        )
        player_to_edit.psid = st.text_input(
            "PSID",
            key="edit_psid",
            help="Zostaw puste, jeśli zawodnik nie jest połączony z systemem powiadomień.",
        )
        player_to_edit.user_email = st.text_input(
            "Email użytkownika",
            key="edit_user_email",
            help="Zostaw puste, jeśli zawodnik nie jest połączony z żadnym użytkownikiem.",
        )
        submit = st.button("Zapisz")
        if submit:
            try:
                edit_player(player_to_edit)
            except Exception as e:
                st.session_state.notification = {"msg": str(e), "icon": "❌"}
            else:
                st.session_state.notification = {
                    "icon": "✅",
                    "msg": f"Zawodnik '{player_to_edit.fullname}' zedytowany!",
                }
            finally:
                st.rerun()


with st.container(border=True):
    st.subheader("Usuń zawodnika", text_alignment="center")
    player_to_delete = st.selectbox(
        "Wybierz zawodnika",
        index=None,
        format_func=lambda p: p.fullname,
        key="delete_player",
        options=players,
    )
    if player_to_delete:
        submit = st.button("Usuń")
        if submit:
            try:
                delete_player(player_to_delete)
            except Exception as e:
                st.session_state.notification = {"msg": str(e), "icon": "❌"}
            else:
                st.session_state.notification = {
                    "icon": "✅",
                    "msg": f"Zawodnik '{player_to_delete.fullname}' usunięty!",
                }
            finally:
                st.rerun()
