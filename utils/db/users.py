from typing import TypedDict

import streamlit as st
from pymongo.collection import Collection

from utils.db.client import get_client

client = get_client()

class User(TypedDict):
    email: str
    name: str
    role: str

def get_logged_user() -> None:
    """Pull user data from the collection.

    Uses `st.cache_data` to only rerun when the query changes or after 10 min.
    """
    @st.cache_data(ttl=600)
    def _get_logged_user(email: str) -> User | None:
        collection: Collection[User] = client.t27app.users
        users = collection.find(filter={"email": email})
        user = next(users, None)
        return user

    if st.user.is_logged_in:
        st.session_state.db_user = _get_logged_user(str(st.user.email))
    else:
        st.session_state.db_user = None

@st.cache_data(ttl=600)
def get_all_users() -> list[User]:
    """Pull all users from the collection.

    Uses `st.cache_data` to only rerun when the query changes or after 10 min.
    """
    collection: Collection[User] = client.t27app.users
    users = collection.find()
    items_l = list(users)
    return items_l
