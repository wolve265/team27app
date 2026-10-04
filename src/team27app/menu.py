from pathlib import Path

import streamlit as st
from st_social_media_links import SocialMediaIcons

from team27app.utils.db.users import User, UserRole, get_db_user

social_media_links = [
    "https://www.facebook.com/groups/1501886206715210",
    "https://www.instagram.com/__team27__/",
]
notifications_url = "https://www.facebook.com/share/1CoAyMar8S/"

pages_dir = Path("src/team27app/pages")


def home_page() -> None:
    st.set_page_config(
        page_title="Team27App - Strona główna",
        page_icon="⚽",
    )
    get_db_user()
    menu()
    st.header("Team 27 Mielec", divider=True, text_alignment="center")
    st.image("images/t27_logo_white_long.png")
    st.markdown("""
    AZP Team 27 Mielec powstał 27 lipca 2010 roku.

    W sierpniu 2021 pozyskaliśmy PIERWSZEGO historycznego sponsora - "AGRO-DOM".

    Drugiego sponsora Noid Bistro&Catering pozyskaliśmy w grudniu 2025 r.""")


PAGES = {
    "home": st.Page(home_page, title="Strona główna", icon=":material/home:"),
    "login": st.Page(pages_dir / "login.py", title="Zaloguj się"),
    "logout": st.Page(pages_dir / "logout.py", title="Wyloguj się"),
    "games_26_27": st.Page(pages_dir / "games_26_27.py", title="2026/2027"),
    "games_25_26": st.Page(pages_dir / "games_25_26.py", title="2025/2026"),
    "manage_users": st.Page(pages_dir / "manage_users.py", title="Użytkownicy"),
    "manage_players": st.Page(pages_dir / "manage_players.py", title="Zawodnicy"),
    "manage_games": st.Page(pages_dir / "manage_games.py", title="Gierki"),
    "manage_payments": st.Page(pages_dir / "manage_payments.py", title="Płatności"),
    "manage_transactions": st.Page(pages_dir / "manage_transactions.py", title="Transakcje"),
    "paymaster_view": st.Page(pages_dir / "paymaster_view.py", title="Widok skarbnika"),
    "no_permission_redirect": st.Page(
        pages_dir / "no_permission_redirect.py", title="Brak uprawnień"
    ),
}


def menu() -> None:
    """Determine if a user is logged in or not, then show the correct navigation menu."""
    with st.sidebar:
        # User menu
        if not st.user.is_logged_in:
            with st.expander("Witaj nieznajomy", expanded=True, icon=":material/account_box:"):
                st.page_link(PAGES["login"], label="Zaloguj się", icon=":material/login:")
        else:
            with st.expander(f"Witaj {st.user.name}", icon=":material/account_box:"):
                st.page_link(PAGES["logout"], label="Wyloguj się", icon=":material/logout:")

        st.title("Aplikacja Team 27", text_alignment="center")

        # Main menu
        st.page_link(PAGES["home"], label="Strona główna", icon=":material/home:")

        # Indoor games
        with st.expander("Hala", expanded=True, icon=":material/sports_soccer:"):
            st.page_link(PAGES["games_26_27"], label="2026/2027")
            st.page_link(PAGES["games_25_26"], label="2025/2026")

        # Admin menu
        db_user: User = st.session_state.db_user
        if db_user.role is UserRole.ADMIN:
            with st.expander("Admin menu", expanded=True, icon=":material/admin_panel_settings:"):
                st.page_link(
                    PAGES["manage_users"],
                    label="Użytkownicy",
                    icon=":material/supervised_user_circle:",
                )
                st.page_link(
                    PAGES["manage_players"],
                    label="Zawodnicy",
                    icon=":material/directions_run:",
                )
                st.page_link(
                    PAGES["manage_games"],
                    label="Gierki",
                    icon=":material/sports_soccer:",
                )
                st.page_link(
                    PAGES["manage_payments"],
                    label="Płatności",
                    icon=":material/attach_money:",
                )
                st.page_link(
                    PAGES["manage_transactions"],
                    label="Transakcje",
                    icon=":material/payments:",
                )
                st.page_link(
                    PAGES["paymaster_view"],
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
        st.switch_page(PAGES["no_permission_redirect"])
    menu()
