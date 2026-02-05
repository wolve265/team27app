from __future__ import annotations

from datetime import date

import streamlit as st

from lib.auth import auth_bootstrap, ensure_authenticated
from lib.db import list_payments

st.set_page_config(page_title="Payments Summary", page_icon="💳", layout="wide")

auth_bootstrap()

st.title("Payments Summary")

if not ensure_authenticated(show_ui=True):
    st.stop()

user = st.session_state.get("user") or {}
email = user.get("email")

payments = list_payments(email)

if not payments:
    st.info("Brak płatności.")
else:
    rows = []
    total_paid = 0
    total_due = 0
    late_count = 0
    today = date.today().isoformat()

    for p in payments:
        amount = float(p.get("amount", 0))
        status = p.get("status", "pending")
        due_date = p.get("due_date")

        if status == "paid":
            total_paid += amount
        else:
            total_due += amount
            if due_date and due_date < today:
                late_count += 1

        rows.append(
            {
                "Date": p.get("date"),
                "Due": due_date,
                "Amount": amount,
                "Status": status,
                "Method": p.get("method"),
            }
        )

    st.metric("Paid", f"{total_paid:.2f}")
    st.metric("Due", f"{total_due:.2f}")
    st.metric("Late", late_count)

    st.dataframe(rows, use_container_width=True)
