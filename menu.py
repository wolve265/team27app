import streamlit as st

from utils.db.users import User, UserRole, get_db_user


def menu() -> None:
    """Determine if a user is logged in or not, then show the correct navigation menu."""
    with st.sidebar:
        # User menu
        if not st.user.is_logged_in:
            with st.expander("Witaj nieznajomy", expanded=True, icon=":material/account_box:"):
                st.page_link("pages/login.py", label="Zaloguj się", icon=":material/login:")
        else:
            with st.expander(f"Witaj {st.user.name}", icon=":material/account_box:"):
                st.page_link("pages/logout.py", label="Wyloguj się", icon=":material/logout:")

        st.title("Aplikacja Team 27", text_alignment="center")

        # Main menu
        st.page_link("streamlit_app.py", label="Strona główna", icon=":material/home:")

        # Notifications menu

        # Admin menu
        db_user: User = st.session_state.db_user
        if db_user["role"] in {UserRole.ADMIN, UserRole.SUPERADMIN}:
            with st.expander("Admin menu", expanded=True, icon=":material/admin_panel_settings:"):
                st.page_link("pages/manage_users.py", label="Użytkownicy", icon=":material/supervised_user_circle:")
                st.page_link("pages/manage_players.py", label="Zawodnicy", icon=":material/sports_soccer:")

def menu_with_redirect(roles: list[str] = UserRole.list_all_with_superadmin()) -> None:
    """Redirect users to the main page if not correct role.

    Otherwise continue to render the navigation menu.
    """
    get_db_user()

    if st.session_state.db_user["role"] not in roles:
        st.switch_page("pages/no_permission_redirect.py")
    menu()
