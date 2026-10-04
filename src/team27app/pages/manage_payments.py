import datetime

import streamlit as st
from pydantic.fields import FieldInfo

from team27app.menu import menu_with_redirect
from team27app.utils.db.payments import Payment, get_payments_repo
from team27app.utils.db.players import get_players_repo
from team27app.utils.db.users import UserRole
from team27app.utils.pages import ToastNotifications, execute_with_toast, set_page
from team27app.utils.seasons import merge_seasons, st_seasons
from team27app.utils.streamlit.crud import (
    CrudSpec,
    render_add_form,
    render_delete_form,
    render_edit_form,
)

PAGE_NAME = "Zarządzanie płatnościami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN])
ToastNotifications.render()

season = merge_seasons(st_seasons())

payments_repo = get_payments_repo()
players_repo = get_players_repo()

payments = sorted(
    payments_repo.find_by(season.get_datetime_query()), key=lambda pay: str(pay.id), reverse=True
)
players = sorted(players_repo.find_by({}), key=lambda p: p.surname)


def _render_payment_player(
    field_name: str, widget_key: str, field: FieldInfo, value: str | None
) -> str | None:
    """Map the stored player ID to a player option for the selectbox widget."""
    initial_player = next(
        (player for player in players if str(player.id) == value),
        None,
    )
    selected_player = st.selectbox(
        field.title or "Zawodnik",
        index=players.index(initial_player) if initial_player else None,
        options=players,
        key=widget_key,
        help=field.description,
        format_func=lambda player: player.fullname,
    )
    return str(selected_player.id) if selected_player else None


payments_crud = CrudSpec(
    model=Payment,
    objects=payments,
    save=payments_repo.save,
    delete=payments_repo.delete,
    format_func=lambda payment: payment.format(players),
    add_values={
        "datetime": datetime.datetime.now(tz=datetime.UTC).replace(
            hour=12, minute=0, second=0, microsecond=0
        ),
        "value": 0,
    },
    field_renderers={"player_id": _render_payment_player},
)


with st.expander("Płatności", expanded=True):
    st.button("Odśwież")
    cols = st.columns(2)
    cols[0].write(f"Liczba płatności: {len(payments)}")
    cols[1].write(f"Suma płatności: {sum([pay.value for pay in payments])} zł")
    payments_to_show = [
        {
            "Data": pay.date,
            "Kto": (player := next(p for p in players if str(p.id) == pay.player_id)).fullname,
            "Ile": f"{pay.value} zł",
        }
        for pay in payments
    ]
    st.dataframe(payments_to_show)

new_payment = render_add_form(
    payments_crud,
    key="payment_add",
    title="Dodaj płatność",
)
if new_payment:
    with execute_with_toast(f"Płatność '{new_payment.format(players)}' dodana!"):
        payments_repo.save(new_payment)
    st.rerun()


edited_payment = render_edit_form(
    payments_crud,
    key="payment_edit",
    title="Edytuj płatność",
    select_label="Wybierz płatność",
)
if edited_payment:
    with execute_with_toast(f"Płatność '{edited_payment.format(players)}' zedytowana!"):
        payments_repo.save(edited_payment)
    st.rerun()


deleted_payments = render_delete_form(
    payments_crud,
    key="payment_delete",
    title="Usuń płatność",
    select_label="Wybierz płatność/płatności",
)
if deleted_payments:
    for payment_to_delete in deleted_payments:
        with execute_with_toast(f"Płatność '{payment_to_delete.format(players)}' usunięta!"):
            payments_repo.delete(payment_to_delete)
    st.rerun()
