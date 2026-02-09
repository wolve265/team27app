from dataclasses import dataclass

import requests
import streamlit as st


@dataclass(frozen=True, unsafe_hash=True)
class Participant:
    psid: str
    name: str


class Api:
    """
    A class to handle API interactions for the Facebook Messenger bot.
    """

    API_URL = st.secrets["fb"].get("meta_graph_api_url")
    ACCESS_TOKEN = st.secrets["fb"].get("meta_access_token")

    def get_all_unique_participants(self) -> list[Participant]:
        """
        Retrieve all unique participants who have interacted with the fanpage.

        Returns:
            list of unique Participant objects or error dict
        """
        participants: list[Participant] = []

        response = requests.get(
            url=f"{self.API_URL}/me/conversations",
            params={"access_token": self.ACCESS_TOKEN, "fields": "participants"},
            timeout=10,
        )

        for conversation in response.json().get("data", []):
            for participant_data in conversation.get("participants", {}).get("data", []):
                participant = Participant(
                    psid=participant_data.get("id"),
                    name=participant_data.get("name"),
                )
                if participant not in participants:
                    participants.append(participant)
        return participants

    def send_message(self, user_psid: str, message_text: str) -> None:
        """
        Send message via Facebook Messenger using Meta Graph API.

        IMPORTANT: You can send messages only to:
        - users who have previously interacted with your page

        Args:
            user_psid: User PSID (Page-Scoped ID)
            message_text: Message text to send
        """
        _response = requests.post(
            url=f"{self.API_URL}/me/messages",
            json={
                "recipient": {"id": user_psid},
                "message": {"text": message_text},
            },
            params={"access_token": self.ACCESS_TOKEN},
            timeout=10,
        )
