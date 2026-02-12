import streamlit as st

from menu import menu_with_redirect
from utils.pages import set_page

PAGE_NAME = "Zaloguj się"
set_page(PAGE_NAME)

menu_with_redirect()

st.button("Zaloguj", on_click=st.login)
