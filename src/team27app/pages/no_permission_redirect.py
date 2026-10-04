import time

import streamlit as st

from team27app.menu import PAGES, menu
from team27app.utils.pages import set_page

PAGE_NAME = "Brak uprawnień!"
set_page(PAGE_NAME)

menu()

st.warning("Nie masz uprawnień, aby zobaczyć tę stronę! Zostaniesz przekierowany na stronę główną.")
st.button("Przekieruj teraz", on_click=lambda: st.switch_page(PAGES["home"]))
msg = st.empty()
for i in range(5, 0, -1):
    msg.text(f"Przekierowanie za {i} sekund...")
    time.sleep(1)
st.switch_page(PAGES["home"])
