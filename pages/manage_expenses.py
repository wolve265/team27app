import streamlit as st

from menu import menu_with_redirect
from utils.db.expenses import Expense, get_expenses_repo
from utils.db.users import UserRole
from utils.pages import ToastNotifications, execute_with_toast, set_page

PAGE_NAME = "Zarządzanie wydatkami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])
ToastNotifications.render()


expenses_repo = get_expenses_repo()

expenses = sorted(expenses_repo.find_by({}), key=lambda expense: str(expense.id), reverse=True)


with st.expander("Wydatki", expanded=True):
    st.button("Odśwież")
    cols = st.columns(2)
    cols[0].write(f"Liczba wydatków: {len(expenses)}")
    cols[1].write(f"Suma wydatków: {sum([e.value for e in expenses])} zł")
    expenses_to_show = [
        {
            "Co?": e.name,
            "Ile?": f"{e.value} zł",
        }
        for e in expenses
    ]
    st.dataframe(expenses_to_show)

with st.form("add_expense_form"):
    st.subheader("Dodaj wydatek", text_alignment="center")
    name = st.text_input("Nazwa wydatku", max_chars=255).strip()
    value = st.number_input("Kwota (zł)", min_value=0, max_value=None)
    submit = st.form_submit_button("Dodaj")
    if submit:
        expense = Expense(name=name, value=value)
        with execute_with_toast(f"Wydatek '{expense.name}' dodany!"):
            expenses_repo.save(expense)
        st.rerun()


def update_edit_expense_form() -> None:
    if "edit_expense" not in st.session_state:
        return
    if not st.session_state.edit_expense:
        return
    expense: Expense = st.session_state["edit_expense"]
    st.session_state.edit_value = expense.value


with st.container(border=True):
    st.subheader("Edytuj wydatek", text_alignment="center")
    expense_to_edit = st.selectbox(
        "Wybierz wydatek",
        index=None,
        format_func=lambda e: e.name,
        key="edit_expense",
        options=expenses,
        on_change=update_edit_expense_form,
    )
    if expense_to_edit:
        expense_to_edit.value = st.number_input(
            "Kwota (zł)",
            key="edit_value",
            min_value=0,
            max_value=None,
        )
        submit = st.button("Zapisz")
        if submit:
            with execute_with_toast(f"Wydatek '{expense_to_edit.name}' zedytowany!"):
                expenses_repo.save(expense_to_edit)
            st.rerun()


with st.container(border=True):
    st.subheader("Usuń wydatek", text_alignment="center")
    expenses_to_delete = st.multiselect(
        "Wybierz wydatek/wydatki",
        options=expenses,
        format_func=lambda e: e.name,
        key="delete_expense",
    )
    if expenses_to_delete:
        submit = st.button("Usuń")
        if submit:
            for expense_to_delete in expenses_to_delete:
                with execute_with_toast(f"Wydatek '{expense_to_delete.name}' usunięty!"):
                    expenses_repo.delete(expense_to_delete)
            st.rerun()
