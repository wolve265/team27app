import streamlit as st

from lib.auth import auth_bootstrap, ensure_authenticated
from lib.db import list_games

st.set_page_config(page_title="Games History", page_icon="📜", layout="wide")

auth_bootstrap()

st.title("Games History")

if not ensure_authenticated(show_ui=True):
    st.stop()

user = st.session_state.get("user") or {}
email = user.get("email")

if not email:
    st.error("Brak emailu użytkownika.")
    st.stop()

games = list_games(email)

if not games:
    st.info("Brak historii gier.")
else:
    rows = []
    for g in games:
        rows.append(
            {
                "ID": g.get("_id"),
                "Date": g.get("date"),
                "Opponent": g.get("opponent"),
                "Score": g.get("score"),
                "Notes": g.get("notes"),
                "Created": g.get("created_at"),
            }
        )
    st.dataframe(rows, use_container_width=True)
