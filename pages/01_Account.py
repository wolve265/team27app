import streamlit as st

from lib.auth import auth_bootstrap, ensure_authenticated, render_local_login, render_logout

st.set_page_config(page_title="Account", page_icon="👤", layout="wide")

auth_bootstrap()

st.title("Account")

if ensure_authenticated(show_ui=True):
    user = st.session_state.get("user") or {}
    st.success("Zalogowano")
    col1, col2 = st.columns([1, 2])
    with col1:
        if user.get("picture"):
            st.image(user["picture"], width=96)
    with col2:
        st.write(f"**Name:** {user.get('name')}")
        st.write(f"**Email:** {user.get('email')}")
        st.write(f"**Provider:** {user.get('provider')}")

    render_logout()
else:
    st.info("Użyj Google Login poniżej.")
    with st.expander("Local login (opcjonalne)"):
        render_local_login()
