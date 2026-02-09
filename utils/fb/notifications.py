from utils.db.players import Player, is_player_linked_to_messenger
from utils.fb.api import Api

DEFAULT_NOTIFICATION = "Hej, to jest test! Przypominam o wpłacie {amount}zł za zaległe gierki."

api = Api()


def send_cash_notification(player: Player, amount: str) -> None:
    if not is_player_linked_to_messenger(player):
        raise RuntimeError("Zawodnik nie jest połączony z systemem powiadomień!")
    notification = DEFAULT_NOTIFICATION.format(amount=amount)
    api.send_message(user_psid=player["psid"], message_text=notification)
