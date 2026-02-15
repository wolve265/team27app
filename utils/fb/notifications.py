import streamlit as st

from utils.db.players import Player, is_player_linked_to_messenger
from utils.fb.api import Api

PHONE_NUMBER = st.secrets["contact"].get("paymaster")

NOTIFICATION = """
Hej, przypominam o wpłacie {amount} zł za zaległe gierki.

💸 BLIK: {phone_number}

Ta wiadomość jest automatyczna. Proszę na nią nie odpowiadać.
W razie problemów skontaktuj się z programistą i/lub skarbnikiem Team27.
"""

api = Api()


def send_cash_notification(player: Player, amount: int) -> str:
    if not is_player_linked_to_messenger(player):
        raise RuntimeError(f"Zawodnik {player.fullname} nie jest połączony z systemem powiadomień!")
    notification = NOTIFICATION.format(amount=amount, phone_number=PHONE_NUMBER)
    api.send_message(user_psid=player.psid, message_text=notification)
    return notification
