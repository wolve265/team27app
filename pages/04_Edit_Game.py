from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from lib.auth import auth_bootstrap, ensure_authenticated
from lib.db import list_games, update_game

st.set_page_config(page_title="Edit Game", page_icon="✏️", layout="wide")

auth_bootstrap()

st.title("Edit Game")

if not ensure_authenticated(show_ui=True):
    st.stop()

user = st.session_state.get("user") or {}
email = user.get("email")

games = list_games(email)
if not games:
    st.info("Brak gier do edycji.")
    st.stop()

options = {f"{g.get('date')} vs {g.get('opponent')} ({g.get('_id')})": g for g in games}
selected_label = st.selectbox("Select game", list(options.keys()))
selected = options[selected_label]

with st.form("edit_game_form"):
    date = st.date_input("Date", value=datetime.fromisoformat(selected.get("date")).date())
    opponent = st.text_input("Opponent", value=selected.get("opponent", ""))
    score = st.text_input("Score", value=selected.get("score", ""))
    notes = st.text_area("Notes", value=selected.get("notes", ""))
    submitted = st.form_submit_button("Update")

if submitted:
    update_game(
        selected.get("_id"),
        email,
        {
            "date": date.isoformat(),
            "opponent": opponent,
            "score": score,
            "notes": notes,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    st.success("Game updated.")
