import streamlit as st

from lib.auth import auth_bootstrap, ensure_authenticated
from lib.db import delete_game, list_games

st.set_page_config(page_title="Remove Game", page_icon="🗑️", layout="wide")

auth_bootstrap()

st.title("Remove Game")

if not ensure_authenticated(show_ui=True):
    st.stop()

user = st.session_state.get("user") or {}
email = user.get("email")

games = list_games(email)
if not games:
    st.info("Brak gier do usunięcia.")
    st.stop()

options = {f"{g.get('date')} vs {g.get('opponent')} ({g.get('_id')})": g for g in games}
selected_label = st.selectbox("Select game", list(options.keys()))
selected = options[selected_label]

confirm = st.checkbox("Confirm removal")
if st.button("Remove"):
    if confirm:
        delete_game(selected.get("_id"), email)
        st.success("Game removed.")
    else:
        st.warning("Please confirm removal.")
