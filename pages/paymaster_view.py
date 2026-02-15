import streamlit as st

from menu import menu_with_redirect
from utils.db.games import get_games_repo, get_player_games, get_player_games_cost
from utils.db.payments import get_payments_repo, get_player_payments_sum
from utils.db.players import get_players_repo
from utils.db.users import UserRole
from utils.fb.api import Api
from utils.fb.notifications import send_cash_notification
from utils.pages import ToastNotifications, set_page
from utils.player_info import PlayerInfo

PAGE_NAME = "Widok skarbnika"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])

games_repo = get_games_repo()
payments_repo = get_payments_repo()
players_repo = get_players_repo()

games = sorted(games_repo.find_by({}), key=lambda g: g.datetime, reverse=True)
players = sorted(players_repo.find_by({}), key=lambda p: p.surname)
payments = list(payments_repo.find_by({}))

avg_game_cost = round(sum([g.cost for g in games]) / len(games))
players_infos = [PlayerInfo.from_player(p, games, payments) for p in players]

tab_names = [
    "Podsumowanie płatności",
    "Przypomnij o zaległych wpłatach",
    "Pozostałe - eksperymentalne",
]
summary_tab, notify_tab, rest_tab = st.tabs(tab_names)

toast_notifications = ToastNotifications()


with summary_tab:
    with st.expander("Zawodnicy - podsumowanie płatności", expanded=True):
        st.button("Odśwież")
        all_games_cost = sum([g.cost * g.players_count for g in games])
        all_players_payment = sum([pay.value for pay in payments])
        cols = st.columns(3)
        cols[0].write(f"Całkowity koszt: {all_games_cost} zł")
        cols[1].write(f"Razem wpłat: {all_players_payment} zł")
        all_balance = all_players_payment - all_games_cost
        color_balance = "red" if all_balance < 0 else "green"
        cols[2].write(f"Bilans: :{color_balance}[{all_balance} zł]")
        players_to_show = [
            {
                "Zawodnik": p.fullname,
                "Liczba gierek": len(get_player_games(games, p)),
                "Zapłacono?": (pay_sum := get_player_payments_sum(payments, p))
                >= (game_cost := get_player_games_cost(games, p)),
                "Suma wpłat": pay_sum,
                "Koszt gierek": game_cost,
                "Bilans": (balance := pay_sum - game_cost),
                "Gry opłacone z góry": balance // avg_game_cost,
            }
            for p in players
        ]
        st.dataframe(sorted(players_to_show, key=lambda x: x["Bilans"]))


with notify_tab:
    late_players_infos = [pi for pi in players_infos if pi.balance < 0]
    players_to_show = [
        {
            "Zawodnik": pi.player.fullname,
            "Bilans": pi.balance,
        }
        for pi in late_players_infos
    ]
    st.dataframe(players_to_show)

    submit = st.button("Przypomnij wszystkim")
    if submit:
        for pi in late_players_infos:
            try:
                notification = send_cash_notification(pi.player, abs(pi.balance))
            except Exception as e:
                toast_notifications.add(msg=str(e), icon="❌")
            else:
                toast_notifications.add(
                    msg=f"Powiadomienie do '{pi.player.fullname}' zostało wysłane!", icon="✅"
                )
        st.rerun()


with rest_tab:
    with st.container(border=True):
        st.warning("Ta funkcjonalność jest eksperymentalna")
        submit = st.button("Pobierz wszystkich korespondentów")
        if submit:
            api = Api()
            ps = api.get_all_unique_participants()
            st.dataframe(ps)

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
        submit = False
        if player_to_notify:
            amount = st.number_input("Kwota do zapłaty (zł)", key="notify_amount", min_value=0)
            submit = st.button("Wyślij powiadomienie")
            if submit:
                if not amount:
                    st.error("Kwota jest wymagana!")
                else:
                    try:
                        send_cash_notification(player_to_notify, amount)
                    except Exception as e:
                        toast_notifications.add(msg=str(e), icon="❌")
                    else:
                        toast_notifications.add(
                            icon="✅",
                            msg=f"Powiadomienie do '{player_to_notify.fullname}' zostało wysłane!",
                        )
                    finally:
                        st.rerun()
