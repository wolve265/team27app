import streamlit as st

from menu import menu_with_redirect

menu_with_redirect()

st.header("Zaloguj się")
st.button("Zaloguj", on_click=st.login)
