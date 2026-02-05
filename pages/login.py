import streamlit as st

st.header("Log in")
# role = st.selectbox("Choose your role", ROLES)

st.button("Log in", on_click=st.login)
