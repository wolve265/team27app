import streamlit as st

from menu import menu
from utils.db.users import get_db_user

st.set_page_config(
    page_title="Team27App - Strona główna",
    page_icon="⚽",
)

get_db_user()

# Sidebar and menu
menu()

# Main page content
st.header("Team 27 Mielec", divider=True, text_alignment="center")
st.image("images/t27_logo_white_long.png")
st.markdown("""
AZP Team 27 Mielec powstał 27 lipca 2010 roku.

W sierpniu 2021 pozyskaliśmy PIERWSZEGO historycznego sponsora - "AGRO-DOM".

Drugiego sponsora Noid Bistro&Catering pozyskaliśmy w grudniu 2025 r.""")
