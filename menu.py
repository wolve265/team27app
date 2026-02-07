import streamlit as st

from utils.db.users import User, UserRole, get_db_user


def menu() -> None:
    """Determine if a user is logged in or not, then show the correct navigation menu."""
    with st.sidebar:
        st.title("Team 27 App", text_alignment="center")
        st.page_link("streamlit_app.py", label="Home", icon=":material/home:")

        if not st.user.is_logged_in:
            with st.expander("Hi viewer", expanded=True, icon=":material/account_box:"):
                st.page_link("pages/login.py", label="Log in", icon=":material/login:")
        else:
            with st.expander(f"Hi {st.user.name}", icon=":material/account_box:"):
                st.page_link("pages/logout.py", label="Log out", icon=":material/logout:")

        db_user: User = st.session_state.db_user
        if db_user["role"] in {UserRole.ADMIN, UserRole.SUPERADMIN}:
            with st.expander("Admin menu", expanded=True, icon=":material/admin_panel_settings:"):
                st.page_link("pages/users.py", label="Manage users")

def menu_with_redirect(roles: list[str] = UserRole.list_all()) -> None:
    """Redirect users to the main page if not correct role.

    Otherwise continue to render the navigation menu.
    """
    get_db_user()

    if st.session_state.db_user["role"] not in roles:
        st.warning("You don't have permission to view this page!")
        st.switch_page("streamlit_app.py")
    menu()
