from __future__ import annotations

from datetime import date, datetime, timezone

import streamlit as st

from lib.auth import auth_bootstrap, ensure_authenticated
from lib.db import insert_payment_event, list_payments

st.set_page_config(page_title="Send Late Notification", page_icon="📣", layout="wide")

auth_bootstrap()

st.title("Send Late Notification")

if not ensure_authenticated(show_ui=True):
    st.stop()

user = st.session_state.get("user") or {}
email = user.get("email")

payments = list_payments(email)

late = []
if payments:
    today = date.today().isoformat()
    for p in payments:
        if p.get("status") != "paid" and p.get("due_date") and p.get("due_date") < today:
            late.append(p)

if not late:
    st.info("Brak zaległych płatności.")
else:
    st.warning(f"Zaległe płatności: {len(late)}")
    if st.button("Send notification (mock)"):
        insert_payment_event(
            {
                "email": email,
                "count": len(late),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "type": "late_payment_notification",
            }
        )
        st.success("Wysłano powiadomienie (mock).")
