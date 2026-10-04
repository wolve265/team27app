import streamlit as st

from team27app.menu import menu_with_redirect
from team27app.utils.pages import set_page

PAGE_NAME = "Zaloguj się"
set_page(PAGE_NAME)

menu_with_redirect()

st.button("Zaloguj", on_click=st.login)
