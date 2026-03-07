import streamlit as st

from menu import menu_with_redirect
from utils.db.games import get_games_repo
from utils.db.payments import Payment, get_payments_repo
from utils.db.players import get_players_repo
from utils.db.transactions import Transaction, get_transactions_repo
from utils.db.users import UserRole
from utils.fb.api import Api
from utils.fb.notifications import send_cash_notification
from utils.pages import ToastNotifications, execute_with_toast, set_page
from utils.player_info import PlayerInfo

PAGE_NAME = "Widok skarbnika"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])
ToastNotifications.render()


transactions_repo = get_transactions_repo()
games_repo = get_games_repo()
payments_repo = get_payments_repo()
players_repo = get_players_repo()

transactions = list(transactions_repo.find_by({}))
games = sorted(games_repo.find_by({}), key=lambda g: g.datetime, reverse=True)
players = sorted(players_repo.find_by({}), key=lambda p: p.surname)
payments = list(payments_repo.find_by({}))

avg_game_cost = round(sum([g.cost_per_player for g in games]) / len(games))
players_infos = [PlayerInfo.from_player(p, games, payments) for p in players]

tab_names = [
    "Podsumowanie płatności",
    "Środki zespołu",
    "Przypomnij o zaległych wpłatach",
    "Pozostałe - eksperymentalne",
]
payments_tab, funds_tab, notify_tab, rest_tab = st.tabs(tab_names)


with payments_tab:
    all_players_payments_expected = sum([g.cost_per_player * g.players_count for g in games])
    all_players_payments_current = sum([pay.value for pay in payments])
    all_payments_balance = all_players_payments_current - all_players_payments_expected
    all_payments_balance_color = "red" if all_payments_balance < 0 else "green"

    cols = st.columns(3)
    cols[0].write(f"Suma wpłat: **{all_players_payments_current} zł**")
    cols[1].write(f"Oczekiwana suma wpłat: **{all_players_payments_expected} zł**")
    cols[2].write(f"Bilans wpłat: :{all_payments_balance_color}[{all_payments_balance} zł]")

    players_infos = [PlayerInfo.from_player(p, games, payments) for p in players]
    players_to_show = [
        {
            "Zawodnik": p.fullname,
            "Liczba gierek": pi.game_count,
            "Zapłacono?": pi.game_paid,
            "Suma wpłat": f"{pi.payments_sum} zł",
            "Koszt gierek": f"{pi.games_cost} zł",
            "Bilans": f"{pi.balance} zł",
            "Gry opłacone z góry": pi.balance // avg_game_cost,
        }
        for p, pi in zip(players, players_infos)
    ]
    st.dataframe(sorted(players_to_show, key=lambda x: x["Bilans"]))


with funds_tab:
    all_games_cost = sum([g.cost for g in games])
    games_transaction = Transaction(name="Wynajem hali", value=-all_games_cost)
    payments_transaction = Transaction(
        name="Wpłaty od zawodników", value=all_players_payments_current
    )
    all_transactions = transactions + [games_transaction, payments_transaction]
    revenues = [t for t in all_transactions if t.is_revenue()]
    expenses = [t for t in all_transactions if t.is_expense()]

    revenues_sum = sum([t.value for t in revenues])
    expenses_sum = sum([t.value for t in expenses])

    all_balance = sum([t.value for t in all_transactions])
    all_balance_color = "red" if all_balance < 0 else "green"

    cols = st.columns(3)
    cols[0].write(f"Suma przychodów: **{revenues_sum} zł**")
    cols[1].write(f"Suma wydatków: **{expenses_sum} zł**")
    cols[2].write(f"Saldo zespołu: :{all_balance_color}[{all_balance} zł]")

    funds_to_show = [{"Nazwa": t.name, "Koszt": f"{t.value} zł"} for t in all_transactions]
    st.dataframe(funds_to_show)


with notify_tab:
    late_players_infos = [pi for pi in players_infos if pi.balance < 0]
    players_to_show = [
        {
            "Zawodnik": pi.player.fullname,
            "Bilans": f"{pi.balance} zł",
        }
        for pi in late_players_infos
    ]
    if not players_to_show:
        st.success("Nie ma nikogo z zaległymi wpłatami")
    else:
        event = st.dataframe(players_to_show, on_select="rerun", selection_mode="multi-row")
        selected_rows = event.get("selection", {}).get("rows", [])
        selected_players_count = len(selected_rows)
        cols = st.columns(2)
        remind_selected = cols[0].button(
            f"Przypomnij zaznaczonym ({selected_players_count})",
            help=(
                "Wysyła wiadomość przypominającą na Messengerze do zaznaczonych zawodników,"
                " pod warunkiem, że mają dodany PSID (Facebook Paged Scoped Identifier)"
            ),
            disabled=selected_players_count < 1,
        )
        mark_selected_paid = cols[1].button(
            f"Zaznacz zaznaczonych ({selected_players_count}), że zapłacili",
            help=(
                "Dodaje płatności dla zaznaczonych zawodników."
                " Kwota dodanej płatności będzie taka, aby bilans zawodnika był równy 0."
            ),
            disabled=selected_players_count < 1,
        )
        if remind_selected:
            for i, pi in enumerate(late_players_infos):
                if i in selected_rows:
                    with execute_with_toast(
                        f"Powiadomienie do '{pi.player.fullname}' zostało wysłane!"
                    ):
                        notification = send_cash_notification(pi.player, abs(pi.balance))
            st.rerun()
        if mark_selected_paid:
            for i, pi in enumerate(late_players_infos):
                if i in selected_rows:
                    with execute_with_toast(f"Zawodnik '{pi.player.fullname}' zapłacił!"):
                        payments_repo.save(
                            Payment(player_id=str(pi.player.id), value=abs(pi.balance))
                        )
            st.rerun()


with rest_tab:
    with st.container(border=True):
        api = Api()
        st.warning("Ta funkcjonalność jest eksperymentalna")
        cols = st.columns(2)
        get_all_participants_button = cols[0].button("Pobierz wszystkich korespondentów")
        get_new_participants_button = cols[1].button("Pobierz nowych korespondentów")
        if get_all_participants_button:
            all_participants = api.get_all_unique_participants()
            st.dataframe(all_participants)
        if get_new_participants_button:
            all_participants = api.get_all_unique_participants()
            all_known_psids = {p.psid for p in players}
            new_participants = [pt for pt in all_participants if pt.psid not in all_known_psids]
            st.dataframe(new_participants)

    with st.container(border=True):
        st.subheader("Wyślij powiadomienie o zaległej wpłacie")
        st.warning("Ta funkcjonalność jest eksperymentalna")
        player_to_notify = st.selectbox(
            "Wybierz zawodnika",
            index=None,
            key="notify_player",
            options=players,
            format_func=lambda p: p.fullname,
        )
        if player_to_notify:
            amount = st.number_input("Kwota do zapłaty (zł)", key="notify_amount", min_value=0)
            submit = st.button("Wyślij powiadomienie")
            if submit:
                if not amount:
                    st.error("Kwota jest wymagana!")
                else:
                    with execute_with_toast(
                        f"Powiadomienie do '{player_to_notify.fullname}' zostało wysłane!"
                    ):
                        send_cash_notification(player_to_notify, amount)
                    st.rerun()
