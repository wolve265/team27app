import streamlit as st
from pydantic import BaseModel, Field, computed_field
from pydantic_mongo import AbstractRepository, PydanticObjectId

from utils.db.client import get_db

# from pydantic import EmailStr # TODO: check email str


player_column_config_mapping = {
    "id": None,
    "name": "Imię",
    "surname": "Nazwisko",
    "team27_number": st.column_config.NumberColumn("Numer"),
    "psid": None,
    "user_email": None,
    "fullname": "Imię i nazwisko",
}


class Player(BaseModel):
    id: PydanticObjectId | None = None
    name: str
    surname: str
    team27_number: int = Field(ge=0)
    psid: str
    # user_email: EmailStr
    user_email: str

    @computed_field(repr=False)
    @property
    def fullname(self) -> str:
        return f"{self.name} {self.surname}"


class PlayersRepository(AbstractRepository[Player]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        collection_name = "players"


def get_players_repo() -> PlayersRepository:
    return PlayersRepository(get_db())


def is_player_linked_to_user(player: Player) -> bool:
    """Check if the player is linked to a user."""
    return bool(player.user_email)


def is_player_linked_to_messenger(player: Player) -> bool:
    """Check if the player is linked to a messenger notification system."""
    return bool(player.psid)


def is_player_team27_member(player: Player) -> bool:
    """Check if the player is a member of team 27."""
    return player.team27_number > 0
