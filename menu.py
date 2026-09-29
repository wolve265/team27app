import streamlit as st
from st_social_media_links import SocialMediaIcons

from utils.db.users import User, UserRole, get_db_user

social_media_links = [
    "https://www.facebook.com/groups/1501886206715210",
    "https://www.instagram.com/__team27__/",
]
notifications_url = "https://www.facebook.com/share/1CoAyMar8S/"


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

        # Indoor games
        with st.expander("Hala", expanded=True, icon=":material/sports_soccer:"):
            st.page_link("pages/games_26_27.py", label="2026/2027")
            st.page_link("pages/games_25_26.py", label="2025/2026")

        # Admin menu
        db_user: User = st.session_state.db_user
        if db_user.role is UserRole.ADMIN:
            with st.expander("Admin menu", expanded=True, icon=":material/admin_panel_settings:"):
                st.page_link(
                    "pages/manage_users.py",
                    label="Użytkownicy",
                    icon=":material/supervised_user_circle:",
                )
                st.page_link(
                    "pages/manage_players.py",
                    label="Zawodnicy",
                    icon=":material/directions_run:",
                )
                st.page_link(
                    "pages/manage_games.py",
                    label="Gierki",
                    icon=":material/sports_soccer:",
                )
                st.page_link(
                    "pages/manage_payments.py",
                    label="Płatności",
                    icon=":material/attach_money:",
                )
                st.page_link(
                    "pages/manage_transactions.py",
                    label="Transakcje",
                    icon=":material/payments:",
                )
                st.page_link(
                    "pages/paymaster_view.py",
                    label="Widok skarbnika",
                    icon=":material/finance:",
                )

        # Socials
        st.markdown("---")
        social_html = SocialMediaIcons(social_media_links)._get_html()
        bell_link = (
            f'<a href="{notifications_url}" target="_blank" style="margin-left: -4px;">'
            '<svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" viewBox="0 0 24 24" fill="#808080"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.1-1.6-5.6-4.5-6.3V4c0-.8-.7-1.5-1.5-1.5S10.5 3.2 10.5 4v.7C7.6 5.4 6 7.9 6 11v5l-2 2v1h16v-1l-2-2z"/></svg></a>'
        )
        social_html = social_html.replace("</div>", f"{bell_link}</div>", 1)
        st.markdown(social_html, unsafe_allow_html=True)


default_roles = UserRole.list_all()


def menu_with_redirect(roles: list[UserRole] = default_roles) -> None:
    """Redirect users to the main page if not correct role.

    Otherwise continue to render the navigation menu.
    """
    db_user = get_db_user()

    if db_user.role not in roles:
        st.switch_page("pages/no_permission_redirect.py")
    menu()
