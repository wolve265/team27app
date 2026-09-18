import datetime

import streamlit as st

from menu import menu_with_redirect
from utils.db.seasons import Seasons, merge_seasons
from utils.db.transactions import Transaction, get_transactions_repo
from utils.db.users import UserRole
from utils.pages import ToastNotifications, execute_with_toast, set_page

PAGE_NAME = "Zarządzanie transakcjami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])
ToastNotifications.render()

season = merge_seasons(
    st.pills(
        "Sezony",
        key="selected_seasons",
        options=sorted(Seasons.list_all(), key=lambda s: s.end, reverse=True),
        selection_mode="multi",
        default=Seasons.list_all(),
        format_func=lambda s: s.name,
        persist_state="session",
    )
)

transactions_repo = get_transactions_repo()

transactions = sorted(
    transactions_repo.find_by(season.get_datetime_query()),
    key=lambda transaction: str(transaction.id),
    reverse=True,
)
expenses = [t for t in transactions if t.is_expense()]
revenues = [t for t in transactions if t.is_revenue()]


with st.expander("Transakcje", expanded=True):
    st.button("Odśwież")
    cols = st.columns(2)
    cols[0].write(f"Liczba wydatków: {len(expenses)}")
    cols[0].write(f"Liczba wpływów: {len(revenues)}")
    cols[1].write(f"Suma wydatków: {sum([t.value for t in expenses])} zł")
    cols[1].write(f"Suma wpływów: {sum([t.value for t in revenues])} zł")
    cols[0].write(f"Liczba transakcji: {len(transactions)}")
    cols[1].write(f"Bilans transakcji: {sum([t.value for t in transactions])} zł")
    transactions_to_show = [
        {
            "Data": t.date,
            "Co?": t.name,
            "Ile?": f"{t.value} zł",
        }
        for t in transactions
    ]
    st.dataframe(transactions_to_show)

with st.form("add_transaction_form"):
    st.subheader("Dodaj transakcję", text_alignment="center")
    name = st.text_input("Nazwa transakcji", max_chars=255).strip()
    date = st.date_input("Data", format="DD.MM.YYYY")
    dt = datetime.datetime.combine(date, datetime.time(hour=12), tzinfo=datetime.UTC)
    value = st.number_input("Kwota (zł)", step=1)
    submit = st.form_submit_button("Dodaj")
    if submit:
        transaction = Transaction(datetime=dt, name=name, value=value)
        with execute_with_toast(f"Transakcja '{transaction.name}' dodana!"):
            transactions_repo.save(transaction)
        st.rerun()


def update_edit_transaction_form() -> None:
    if "edit_transaction" not in st.session_state:
        return
    if not st.session_state.edit_transaction:
        return
    transaction: Transaction = st.session_state["edit_transaction"]
    st.session_state.edit_date = transaction.datetime
    st.session_state.edit_value = transaction.value


with st.container(border=True):
    st.subheader("Edytuj transakcję", text_alignment="center")
    transaction_to_edit = st.selectbox(
        "Wybierz transakcję",
        index=None,
        format_func=lambda t: t.name,
        key="edit_transaction",
        options=transactions,
        on_change=update_edit_transaction_form,
    )
    if transaction_to_edit:
        date = st.date_input("Data", key="edit_date", format="DD.MM.YYYY")
        dt = datetime.datetime.combine(date, datetime.time(hour=12), tzinfo=datetime.UTC)
        transaction_to_edit.datetime = dt
        transaction_to_edit.value = st.number_input(
            "Kwota (zł)",
            key="edit_value",
            step=1,
        )
        submit = st.button("Zapisz")
        if submit:
            with execute_with_toast(f"Transakcja '{transaction_to_edit.name}' zedytowana!"):
                transactions_repo.save(transaction_to_edit)
            st.rerun()


with st.container(border=True):
    st.subheader("Usuń transakcję", text_alignment="center")
    transactions_to_delete = st.multiselect(
        "Wybierz transakcję/transakcje",
        options=transactions,
        format_func=lambda t: t.name,
        key="delete_transactions",
    )
    if transactions_to_delete:
        submit = st.button("Usuń")
        if submit:
            for transaction_to_delete in transactions_to_delete:
                with execute_with_toast(f"Transakcja '{transaction_to_delete.name}' usunięta!"):
                    transactions_repo.delete(transaction_to_delete)
            st.rerun()
