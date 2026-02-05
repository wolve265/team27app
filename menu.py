import streamlit as st


def authenticated_menu() -> None:
    """Show a navigation menu for authenticated users."""
    with st.expander(f"Hi {st.user.name}"):
        st.page_link("pages/logout.py", label="Log out", icon=":material/logout:")

    # if st.session_state.role in ["admin", "super-admin"]:
    #     st.sidebar.page_link("pages/admin.py", label="Manage users")
    #     st.sidebar.page_link(
    #         "pages/super-admin.py",
    #         label="Manage admin access",
    #         disabled=st.session_state.role != "super-admin",
    #     )


def unauthenticated_menu() -> None:
    """Show a navigation menu for unauthenticated users."""
    st.sidebar.page_link("pages/login.py", label="Log in", icon=":material/login:")


def menu() -> None:
    """Determine if a user is logged in or not, then show the correct navigation menu."""
    with st.sidebar:
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
