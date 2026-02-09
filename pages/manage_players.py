import streamlit as st

from menu import menu_with_redirect
from utils.db.players import Player, get_all_players
from utils.db.users import UserRole

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])

players: list[Player] = get_all_players()

st.header("Zarządzanie zawodnikami")

if "notification" in st.session_state:
    notification = st.session_state.pop("notification")
    icon = notification["icon"]
    st.toast(notification["msg"], icon=icon)

with st.expander("Zawodnicy", expanded=True):
    st.button("Odśwież")
    st.table(players)

with st.form("add_player_form"):
    st.header("Dodaj zawodnika", text_alignment="center")
    st.warning("Ta funkcjonalność jeszcze nie jest dostępna!")
    submit = st.form_submit_button("Dodaj", disabled=True)


with st.container(border=True):
    st.header("Edytuj zawodnika", text_alignment="center")
    fullname = st.selectbox(
        "Wybierz zawodnika",
        key="edit_player",
        options=[f"{p['name']} {p['surname']}" for p in players],
    )
    if players:
        player = next(p for p in players if f"{p['name']} {p['surname']}" == fullname)
    st.warning("Ta funkcjonalność jeszcze nie jest dostępna!")
    submit = st.button("Zapisz", disabled=True)

with st.container(border=True):
    st.header("Usuń zawodnika", text_alignment="center")
    fullname = st.selectbox(
        "Wybierz zawodnika",
        key="delete_player",
        options=[f"{p['name']} {p['surname']}" for p in players],
    )
    if players:
        player = next(p for p in players if f"{p['name']} {p['surname']}" == fullname)
    st.warning("Ta funkcjonalność jeszcze nie jest dostępna!")
    submit = st.button("Usuń", disabled=True)
