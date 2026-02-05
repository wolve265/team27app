import os

import streamlit as st


def get_secret(key: str, default: str | None = None) -> str | None:
    if key in st.secrets:
        return str(st.secrets[key])
    return os.getenv(key, default)


def require_secret(key: str) -> str:
    value = get_secret(key)
    if not value:
        raise ValueError(f"Missing required secret: {key}")
    return value


def get_database_name() -> str:
    return require_secret("MONGODB_DB_NAME")
