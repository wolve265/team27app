import streamlit as st

from menu import menu_with_redirect
from utils.db.transactions import Transaction, get_transactions_repo
from utils.db.users import UserRole
from utils.pages import ToastNotifications, execute_with_toast, set_page
from utils.seasons import merge_seasons, st_seasons
from utils.streamlit.crud import CrudSpec, render_add_form, render_delete_form, render_edit_form

PAGE_NAME = "Zarządzanie transakcjami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN])
ToastNotifications.render()

season = merge_seasons(st_seasons())

transactions_repo = get_transactions_repo()

transactions = sorted(
    transactions_repo.find_by(season.get_datetime_query()),
    key=lambda transaction: str(transaction.id),
    reverse=True,
)
transactions_crud = CrudSpec(
    model=Transaction,
    objects=transactions,
    save=transactions_repo.save,
    delete=transactions_repo.delete,
    format_func=lambda transaction: transaction.name,
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

new_transaction = render_add_form(
    transactions_crud,
    key="transaction_add",
    title="Dodaj transakcję",
)
if new_transaction:
    with execute_with_toast(f"Transakcja '{new_transaction.name}' dodana!"):
        transactions_repo.save(new_transaction)
    st.rerun()


edited_transaction = render_edit_form(
    transactions_crud,
    key="transaction_edit",
    title="Edytuj transakcję",
    select_label="Wybierz transakcję",
)
if edited_transaction:
    with execute_with_toast(f"Transakcja '{edited_transaction.name}' zedytowana!"):
        transactions_repo.save(edited_transaction)
    st.rerun()


deleted_transactions = render_delete_form(
    transactions_crud,
    key="transaction_delete",
    title="Usuń transakcję",
    select_label="Wybierz transakcję/transakcje",
)
if deleted_transactions:
    for transaction_to_delete in deleted_transactions:
        with execute_with_toast(f"Transakcja '{transaction_to_delete.name}' usunięta!"):
            transactions_repo.delete(transaction_to_delete)
    st.rerun()
