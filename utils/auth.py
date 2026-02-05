from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import streamlit as st
import streamlit_authenticator as stauth
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

from lib.config import get_secret, require_secret
from lib.db import upsert_user

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def auth_bootstrap() -> None:
    st.session_state.setdefault("authentication_status", False)
    st.session_state.setdefault("user", None)


def _get_authenticator() -> stauth.Authenticate:
    credentials = st.secrets.get("AUTH_CREDENTIALS", {"usernames": {}})
    cookie_name = get_secret("AUTH_COOKIE_NAME", "streamlit_auth")
    cookie_key = require_secret("AUTH_COOKIE_KEY")
    expiry_days = int(get_secret("AUTH_COOKIE_EXPIRY_DAYS", "7"))
    preauthorized = st.secrets.get("AUTH_PREAUTHORIZED", [])
    return stauth.Authenticate(credentials, cookie_name, cookie_key, expiry_days, preauthorized)


def _build_google_flow() -> Flow:
    client_id = require_secret("GOOGLE_CLIENT_ID")
    client_secret = require_secret("GOOGLE_CLIENT_SECRET")
    redirect_uri = require_secret("GOOGLE_REDIRECT_URI")
    return Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": [redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )


def _handle_google_callback() -> dict[str, Any] | None:
    code = st.query_params.get("code")
    state = st.query_params.get("state")
    expected_state = st.session_state.get("oauth_state")
    if not code:
        return None
    if expected_state and state and state != expected_state:
        st.error("Invalid OAuth state. Please retry login.")
        return None

    flow = _build_google_flow()
    flow.fetch_token(code=code)

    credentials = flow.credentials
    token = credentials.id_token
    if not token:
        return None

    info = id_token.verify_oauth2_token(token, Request(), require_secret("GOOGLE_CLIENT_ID"))
    user = {
        "email": info.get("email"),
        "name": info.get("name") or info.get("given_name") or info.get("email"),
        "picture": info.get("picture"),
        "provider": "google",
        "last_login": datetime.now(timezone.utc),
    }
    if not user["email"]:
        st.error("Google account does not provide an email address.")
        return None

    upsert_user(user)
    st.query_params.clear()
    return user


def login_with_google_ui() -> None:
    st.subheader("Google Login")
    flow = _build_google_flow()
    auth_url, state = flow.authorization_url(prompt="consent", include_granted_scopes="true")
    st.session_state["oauth_state"] = state
    st.link_button("Login with Google", auth_url)


def ensure_authenticated(show_ui: bool = True) -> bool:
    if st.session_state.get("authentication_status") and st.session_state.get("user"):
        return True

    user = _handle_google_callback()
    if user:
        st.session_state["user"] = user
        st.session_state["authentication_status"] = True
        return True

    if show_ui:
        login_with_google_ui()
        st.info("Zaloguj się przez Google.")
    return False


def render_logout() -> None:
    if st.session_state.get("authentication_status"):
        if st.button("Logout"):
            st.session_state["authentication_status"] = False
            st.session_state["user"] = None
            st.rerun()


def render_local_login() -> None:
    st.subheader("Local login (optional)")
    authenticator = _get_authenticator()
    name, authentication_status, username = authenticator.login("Login", "main")
    if authentication_status:
        st.session_state["authentication_status"] = True
        st.session_state["user"] = {"email": username, "name": name, "provider": "local"}
        st.success("Logged in with local credentials.")
    elif authentication_status is False:
        st.error("Invalid username or password")


__all__ = [
    "auth_bootstrap",
    "ensure_authenticated",
    "login_with_google_ui",
    "render_logout",
    "render_local_login",
]
