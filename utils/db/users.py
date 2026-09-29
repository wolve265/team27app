from enum import StrEnum
from typing import Self

import streamlit as st
from pydantic import BaseModel, EmailStr, Field
from pydantic_mongo import AbstractRepository, PydanticObjectId

from utils.db.client import get_db

user_column_config_mapping = {
    "id": None,
    "email": "Email",
    "role": "Rola",
    "superadmin": "Superadmin",
}


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"

    @classmethod
    def list_all(cls) -> list[Self]:
        return [e for e in cls]


class User(BaseModel):
    id: PydanticObjectId | None = None
    email: EmailStr = Field(
        title="Email", description="Email użytkownika, który będzie logował się do aplikacji"
    )
    role: UserRole = Field(title="Rola", description="Rola użytkownika w aplikacji")
    superadmin: bool = Field(
        default=False,
        title="Superadmin",
        description="Czy użytkownik jest superadminem (ma wszystkie uprawnienia)",
    )


class UsersRepository(AbstractRepository[User]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        collection_name = "users"


def get_users_repo() -> UsersRepository:
    return UsersRepository(get_db())


def get_db_user() -> User:
    """Pull user data from the collection and store in the session.

    Uses `st.cache_data` to only rerun when the query changes or after 10 min.
    """

    @st.cache_data(ttl=600)
    def _get_logged_user(email: str) -> User | None:
        users_repo = get_users_repo()
        users = list(users_repo.find_by({"email": email}))
        return users[0] if users else None

    db_user: User | None = None
    if st.user.is_logged_in:
        db_user = _get_logged_user(str(st.user.email))

    db_user = db_user if db_user else User(email="", role=UserRole.USER)
    st.session_state.db_user = db_user
    return db_user
