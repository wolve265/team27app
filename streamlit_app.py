import streamlit as st

from lib.auth import auth_bootstrap, ensure_authenticated

st.set_page_config(page_title="Games & Payments", page_icon="🎮", layout="wide")

auth_bootstrap()

st.sidebar.title("Navigation")

st.sidebar.markdown("**Account**")
st.sidebar.page_link("pages/01_Account.py", label="Login / Logout")

st.sidebar.markdown("**Games**")
st.sidebar.page_link("pages/02_Games_History.py", label="Games History")
st.sidebar.page_link("pages/03_Add_Game.py", label="Add Game")
st.sidebar.page_link("pages/04_Edit_Game.py", label="Edit Game")
st.sidebar.page_link("pages/05_Remove_Game.py", label="Remove Game")

st.sidebar.markdown("**Payments**")
st.sidebar.page_link("pages/06_Payments_Summary.py", label="Payments Summary")
st.sidebar.page_link("pages/07_Send_Late_Notification.py", label="Send Late Notification")

st.title("Games & Payments")
st.write("Wybierz opcję z nawigacji po lewej stronie.")

st.subheader("Status")
if ensure_authenticated(show_ui=False):
    user = st.session_state.get("user") or {}
    st.success(f"Zalogowano jako: {user.get('email')}")
else:
    st.warning("Nie jesteś zalogowany.")
