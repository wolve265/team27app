import streamlit as st

from menu import menu_with_redirect
from utils.db.players import Player, add_player, get_all_players
from utils.db.users import UserRole

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])

players: list[Player] = get_all_players()
for p in players:
    p.pop("_id")  # type: ignore

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
    name = st.text_input("Imię")
    surname = st.text_input("Nazwisko")
    team27_number = st.number_input(
        "Numer w Team 27",
        min_value=0,
        max_value=99,
        step=1,
        help="Wpisz 0, jeśli zawodnik nie jest członkiem Team 27.",
    )
    psid = st.text_input(
        "PSID", help="Zostaw puste, jeśli zawodnik nie jest połączony z systemem powiadomień."
    )
    user_email = st.text_input(
        "Email użytkownika",
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
            except RuntimeError as e:
                st.session_state.notification = {"msg": str(e), "icon": "❌"}
            else:
                st.session_state.notification = {
                    "icon": "✅",
                    "msg": f"Zawodnik '{name} {surname}' dodany!",
                }
            finally:
                st.rerun()


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
