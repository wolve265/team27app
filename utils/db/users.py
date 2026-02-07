from enum import StrEnum
from typing import TypedDict

import streamlit as st
from pymongo.collection import Collection

from utils.db.client import get_client

client = get_client()

class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

    @classmethod
    def list_all(cls) -> list[str]:
        return [e.value for e in cls if e != cls.SUPERADMIN]

    @classmethod
    def list_all_with_superadmin(cls) -> list[str]:
        return [e.value for e in cls]

class User(TypedDict):
    email: str
    role: UserRole

def get_db_user() -> None:
    """Pull user data from the collection and store in the session.

    Uses `st.cache_data` to only rerun when the query changes or after 10 min.
    """
    @st.cache_data(ttl=600)
    def _get_logged_user(email: str) -> User | None:
        collection: Collection[User] = client.t27app.users
        users = collection.find(filter={"email": email})
        user = next(users, None)
        return user

    db_user: User | None = None
    if st.user.is_logged_in:
        db_user = _get_logged_user(str(st.user.email))

    st.session_state.db_user = db_user if db_user else User(email="", role=UserRole.USER)

def get_all_users() -> list[User]:
    """Pull all users from the collection."""
    collection: Collection[User] = client.t27app.users
    users = collection.find()
    items_l = list(users)
    return items_l

def add_user(user: User) -> None:
    """Add a user to the collection."""
    collection: Collection[User] = client.t27app.users
    users = collection.find()
    if any(u["email"] == user["email"] for u in users):
        raise RuntimeError(f"User with email '{user['email']}' already exists!")
    collection.insert_one(user)

def edit_user_role(email: str, new_role: UserRole) -> None:
    """Edit a user's role in the collection."""
    collection: Collection[User] = client.t27app.users
    collection.update_one({"email": email}, {"$set": {"role": new_role}})

def delete_user(email: str) -> None:
    """Delete a user from the collection."""
    collection: Collection[User] = client.t27app.users
    collection.delete_one({"email": email})
