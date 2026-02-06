import streamlit as st

from utils.db.users import User


def authenticated_menu() -> None:
    """Show a navigation menu for authenticated users."""
    with st.expander(f"Hi {st.user.name}", icon=":material/account_box:"):
        st.page_link("pages/logout.py", label="Log out", icon=":material/logout:")

    db_user: User = st.session_state.db_user
    if db_user["role"] == "admin":
        with st.expander("Admin menu", expanded=True, icon=":material/admin_panel_settings:"):
            st.page_link("pages/users.py", label="Manage users")


def unauthenticated_menu() -> None:
    """Show a navigation menu for unauthenticated users."""
    st.sidebar.page_link("pages/login.py", label="Log in", icon=":material/login:")


def menu() -> None:
    """Determine if a user is logged in or not, then show the correct navigation menu."""
    with st.sidebar:
        st.title("Team 27 App", text_alignment="center")
        st.page_link("streamlit_app.py", label="Home", icon=":material/home:")

        if not st.user.is_logged_in:
            unauthenticated_menu()
            return
        authenticated_menu()


def menu_with_redirect() -> None:
    """Redirect users to the main page if not logged in.

    Otherwise continue to render the navigation menu.
    """
    if not st.user.is_logged_in:
        st.switch_page("streamlit_app.py")
    menu()
