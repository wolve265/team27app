import streamlit as st

from menu import menu_with_redirect

menu_with_redirect()

st.header("Log in")
st.button("Log in", on_click=st.login)
