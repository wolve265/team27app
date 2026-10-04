import streamlit as st

from team27app.menu import PAGES

st.navigation(list(PAGES.values()), position="hidden").run()
