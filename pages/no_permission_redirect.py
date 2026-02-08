import time

import streamlit as st

from menu import menu

menu()

st.header("Brak uprawnień!")
st.warning("Nie masz uprawnień, aby zobaczyć tę stronę! Zostaniesz przekierowany na stronę główną.")
st.button("Przekieruj teraz", on_click=lambda: st.switch_page("streamlit_app.py"))
msg = st.empty()
for i in range(5, 0, -1):
    msg.text(f"Przekierowanie za {i} sekund...")
    time.sleep(1)
st.switch_page("streamlit_app.py")
