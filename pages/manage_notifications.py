import streamlit as st

from menu import menu_with_redirect
from utils.db.players import get_all_players
from utils.db.users import UserRole
from utils.fb.api import Api
from utils.fb.notifications import send_cash_notification

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])

players = get_all_players()
for p in players:
    p.pop("_id")  # type: ignore

if "notification" in st.session_state:
    notification = st.session_state.pop("notification")
    icon = notification["icon"]
    st.toast(notification["msg"], icon=icon)

st.header("Zarządzanie powiadomieniami")

with st.container(border=True):
    st.warning("Ta funkcjonalność jest eksperymentalna")
    submit = st.button("Pobierz wszystkich korespondentów")
    if submit:
        api = Api()
        ps = api.get_all_unique_participants()
        ps


with st.container(border=True):
    st.subheader("Wyślij powiadomienie o zaległej wpłacie")
    st.warning("Ta funkcjonalność jest eksperymentalna")
    fullname = st.selectbox(
        "Wybierz zawodnika",
        index=None,
        key="notify_player",
        options=[f"{p['name']} {p['surname']}" for p in players],
    )
    submit = False
    if fullname:
        player = next(p for p in players if f"{p['name']} {p['surname']}" == fullname)
        amount = st.text_input("Kwota do zapłaty (zł)", key="notify_amount")
        submit = st.button("Wyślij powiadomienie")
    if submit:
        if not amount:
            st.error("Kwota jest wymagana!")
        else:
            try:
                send_cash_notification(player, amount)
            except Exception as e:
                st.session_state.notification = {"msg": str(e), "icon": "❌"}
            else:
                st.session_state.notification = {
                    "icon": "✅",
                    "msg": f"Powiadomienie do '{fullname}' zostało wysłane!",
                }
            finally:
                st.rerun()
