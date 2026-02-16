import streamlit as st

from menu import menu_with_redirect
from utils.db.payments import Payment, get_payments_repo
from utils.db.players import get_players_repo
from utils.db.users import UserRole
from utils.pages import ToastNotifications, execute_with_toast, set_page

PAGE_NAME = "Zarządzanie płatnościami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])
ToastNotifications.render()


payments_repo = get_payments_repo()
players_repo = get_players_repo()

payments = sorted(payments_repo.find_by({}), key=lambda pay: str(pay.id), reverse=True)
players = sorted(players_repo.find_by({}), key=lambda p: p.surname)


with st.expander("Płatności", expanded=True):
    st.button("Odśwież")
    cols = st.columns(2)
    cols[0].write(f"Liczba płatności: {len(payments)}")
    cols[1].write(f"Suma płatności: {sum([pay.value for pay in payments])} zł")
    payments_to_show = [
        {
            "Kto": (player := next(p for p in players if str(p.id) == pay.player_id)).fullname,
            "Ile": f"{pay.value} zł",
        }
        for pay in payments
    ]
    st.dataframe(payments_to_show)

with st.form("add_payment_form"):
    st.subheader("Dodaj płatność", text_alignment="center")
    player = st.selectbox(
        "Wybierz zawodnika",
        index=None,
        options=players,
        format_func=lambda p: p.fullname,
    )
    value = st.number_input("Kwota (zł)", min_value=0, max_value=None)
    submit = st.form_submit_button("Dodaj")
    if submit and player:
        payment = Payment(player_id=str(player.id), value=value)
        with execute_with_toast(f"Płatność '{payment.format(players)}' dodana!"):
            payments_repo.save(payment)
        st.rerun()


def update_edit_payment_form() -> None:
    if "edit_payment" not in st.session_state:
        return
    if not st.session_state.edit_payment:
        return
    payment: Payment = st.session_state["edit_payment"]
    st.session_state.edit_value = payment.value


with st.container(border=True):
    st.subheader("Edytuj płatność", text_alignment="center")
    payment_to_edit = st.selectbox(
        "Wybierz płatność",
        index=None,
        format_func=lambda pay: pay.format(players),
        key="edit_payment",
        options=payments,
        on_change=update_edit_payment_form,
    )
    if payment_to_edit:
        payment_to_edit.value = st.number_input(
            "Kwota (zł)",
            key="edit_value",
            min_value=0,
            max_value=None,
        )
        submit = st.button("Zapisz")
        if submit:
            with execute_with_toast(f"Płatność '{payment_to_edit.format(players)}' zedytowana!"):
                payments_repo.save(payment_to_edit)
            st.rerun()


with st.container(border=True):
    st.subheader("Usuń płatność", text_alignment="center")
    payments_to_delete = st.multiselect(
        "Wybierz płatność/płatności",
        options=payments,
        format_func=lambda pay: pay.format(players),
        key="delete_payment",
    )
    if payments_to_delete:
        submit = st.button("Usuń")
        if submit:
            for payment_to_delete in payments_to_delete:
                with execute_with_toast(
                    f"Płatność '{payment_to_delete.format(players)}' usunięta!"
                ):
                    payments_repo.delete(payment_to_delete)
            st.rerun()
