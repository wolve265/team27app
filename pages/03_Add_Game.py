from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st

from lib.auth import auth_bootstrap, ensure_authenticated
from lib.db import insert_game

st.set_page_config(page_title="Add Game", page_icon="➕", layout="wide")

auth_bootstrap()

st.title("Add Game")

if not ensure_authenticated(show_ui=True):
    st.stop()

user = st.session_state.get("user") or {}
email = user.get("email")

with st.form("add_game_form"):
    date = st.date_input("Date")
    opponent = st.text_input("Opponent")
    score = st.text_input("Score")
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Add")

if submitted:
    if not opponent:
        st.error("Opponent is required.")
    else:
        game = {
            "_id": str(uuid4()),
            "email": email,
            "date": date.isoformat(),
            "opponent": opponent,
            "score": score,
            "notes": notes,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        insert_game(game)
        st.success("Game added.")
