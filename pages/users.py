import streamlit as st

from menu import menu_with_redirect
from utils.db.users import get_all_users

menu_with_redirect()

st.header("Users")
users = get_all_users()
users
