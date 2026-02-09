import streamlit as st

from menu import menu_with_redirect
from utils.db.users import UserRole

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])

st.header("Powiadomienia")

st.warning("Ta strona jest w trakcie tworzenia. Powiadomienia będą dostępne wkrótce!")
