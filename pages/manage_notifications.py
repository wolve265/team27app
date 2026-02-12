import streamlit as st

from menu import menu_with_redirect
from utils.db.players import get_all_players
from utils.db.users import UserRole
from utils.fb.api import Api
from utils.fb.notifications import send_cash_notification
from utils.pages import set_page

PAGE_NAME = "Zarządzanie powiadomieniami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])

players = get_all_players()

if "notification" in st.session_state:
    notification = st.session_state.pop("notification")
    icon = notification["icon"]
    st.toast(notification["msg"], icon=icon)


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
    player_to_notify = st.selectbox(
        "Wybierz zawodnika",
        index=None,
        key="notify_player",
        options=players,
        format_func=lambda p: p.fullname,
    )
    submit = False
    if player_to_notify:
        amount = st.text_input("Kwota do zapłaty (zł)", key="notify_amount")
        submit = st.button("Wyślij powiadomienie")
        if submit:
            if not amount:
                st.error("Kwota jest wymagana!")
            else:
                try:
                    send_cash_notification(player_to_notify, amount)
                except Exception as e:
                    st.session_state.notification = {"msg": str(e), "icon": "❌"}
                else:
                    st.session_state.notification = {
                        "icon": "✅",
                        "msg": f"Powiadomienie do '{player_to_notify.fullname}' zostało wysłane!",
                    }
                finally:
                    st.rerun()
