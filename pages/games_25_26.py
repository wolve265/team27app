
import streamlit as st

from menu import menu_with_redirect
from utils.db.games import Season, get_games_repo
from utils.db.payments import get_payments_repo
from utils.db.players import get_players_repo
from utils.pages import set_page
from utils.player_info import PlayerInfo

PAGE_NAME = "Hala 2025/2026"
set_page(PAGE_NAME)

menu_with_redirect()

games_repo = get_games_repo()
payments_repo = get_payments_repo()
players_repo = get_players_repo()

games = sorted(
    games_repo.find_by({"season": Season.INDOOR_25_26}), key=lambda g: g.datetime, reverse=True
)
players_ids_in_season: set[str] = set()
for g in games:
    for player_id in g.players_ids:
        players_ids_in_season.add(player_id)
players = sorted(players_repo.find_by({}), key=lambda p: p.surname)
players = [p for p in players if str(p.id) in players_ids_in_season]
payments = list(payments_repo.find_by({}))

games_tab, players_tab = st.tabs(["Gierki", "Zawodnicy"])


with games_tab:
    for i, game in enumerate(games):
        expanded = i == 0
        games_since_this_one = [g for g in games if g.datetime <= game.datetime]
        players_in_game = [p for p in players if str(p.id) in game.players_ids]
        players_infos_in_game = [
            PlayerInfo.from_player(p, games_since_this_one, payments) for p in players_in_game
        ]
        game_paid = all([pi.game_paid for pi in players_infos_in_game])
        with st.expander(
            f"{game.date} ({':green[opłacona]' if game_paid else ':red[nieopłacona]'})",
            expanded=expanded,
        ):
            st.subheader(game.date, text_alignment="center")
            left, mid, right = st.columns(3)
            left.write("Liczba zawodników:")
            mid.write(f"Team27 - {len([p for p in players_in_game if p.team27_number])}")
            right.write(f"Ogółem - {len(players_in_game)}")
            players_to_show = [
                {
                    "Imię": p.name,
                    "Nazwisko": p.surname,
                    "Zapłacono?": pi.game_paid,
                    "Dotychczasowa liczba gierek": pi.game_count,
                }
                for p, pi in zip(players_in_game, players_infos_in_game)
            ]
            st.dataframe(players_to_show)


with players_tab:
    all_games_cost = sum([g.cost * g.players_count for g in games])
    avg_game_cost = round(sum([g.cost for g in games]) / len(games))
    all_players_payment = sum([pay.value for pay in payments])
    cols = st.columns(3)
    cols[0].write("Liczba zawodników:")
    cols[1].write(f"Team27 - {len([p for p in players if p.team27_number > 0])}")
    cols[2].write(f"Ogółem - {len(players)}")

    cols[0].write(f"Całkowity koszt: {all_games_cost} zł")
    cols[1].write(f"Razem wpłat: {all_players_payment} zł")
    all_balance = all_players_payment - all_games_cost
    color_balance = "red" if all_balance < 0 else "green"
    cols[2].write(f"Bilans: :{color_balance}[{all_balance} zł]")
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
    st.dataframe(players_to_show)
