import streamlit as st

from menu import menu_with_redirect
from utils.db.users import User, UserRole, get_users_repo, user_column_config_mapping
from utils.pages import ToastNotifications, execute_with_toast, set_page

PAGE_NAME = "Zarządzanie użytkownikami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])
ToastNotifications.render()


users_repo = get_users_repo()

users = list(users_repo.find_by({}))


with st.expander("Użytkownicy", expanded=True):
    st.button("Odśwież")
    st.dataframe(users, column_config=user_column_config_mapping)


with st.form("add_user_form"):
    st.subheader("Dodaj użytkownika", text_alignment="center")
    email = st.text_input("Email")
    role = st.selectbox("Rola", UserRole.list_all())
    submit = st.form_submit_button("Dodaj")
    if submit:
        if not email:
            st.error("Email jest wymagany!")
        else:
            user = User(email=email, role=UserRole(role))
            with execute_with_toast(f"Użytkownik '{user.email}' dodany!"):
                users_repo.save(user)
            st.rerun()


def update_edit_user_form() -> None:
    if "edit_user" not in st.session_state:
        return
    if not st.session_state.edit_user:
        return
    user: User = st.session_state.edit_user
    st.session_state.edit_role = user.role


with st.container(border=True):
    st.subheader("Edytuj użytkownika", text_alignment="center")
    user_to_edit = st.selectbox(
        "Wybierz użytkownika",
        index=None,
        format_func=lambda u: u.email,
        key="edit_user",
        options=users,
        on_change=update_edit_user_form,
    )
    if user_to_edit:
        is_superadmin = user_to_edit.role == UserRole.SUPERADMIN
        if is_superadmin:
            st.warning(f"Nie możesz edytować użytkownika o roli '{UserRole.SUPERADMIN}'!")
        else:
            user_to_edit.role = st.selectbox(
                "Rola",
                key="edit_role",
                options=UserRole.list_all(),
                disabled=is_superadmin,
            )
        submit = st.button("Zapisz", disabled=is_superadmin)
        if submit:
            with execute_with_toast(f"Użytkownik '{user_to_edit.email}' zedytowany!"):
                users_repo.save(user_to_edit)
            st.rerun()


with st.container(border=True):
    st.subheader("Usuń użytkownika", text_alignment="center")
    user_to_delete = st.selectbox(
        "Wybierz użytkownika",
        index=None,
        format_func=lambda u: u.email,
        key="delete_user",
        options=users,
        on_change=update_edit_user_form,
    )
    if user_to_delete:
        is_superadmin = user_to_delete.role == UserRole.SUPERADMIN
        if is_superadmin:
            st.warning(f"Nie możesz usunąć użytkownika o roli '{UserRole.SUPERADMIN}'!")
        submit = st.button("Usuń", disabled=is_superadmin)
        if submit:
            with execute_with_toast(f"Użytkownik '{user_to_delete.email}' usunięty!"):
                users_repo.delete(user_to_delete)
            st.rerun()
