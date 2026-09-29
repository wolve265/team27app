import streamlit as st

from menu import menu_with_redirect
from utils.db.users import User, UserRole, get_users_repo, user_column_config_mapping
from utils.pages import ToastNotifications, execute_with_toast, set_page
from utils.streamlit.crud import CrudSpec, render_add_form, render_delete_form, render_edit_form

PAGE_NAME = "Zarządzanie użytkownikami"
set_page(PAGE_NAME)

menu_with_redirect(roles=[UserRole.ADMIN])
ToastNotifications.render()


users_repo = get_users_repo()

users = list(users_repo.find_by({}))

users_crud = CrudSpec(
    model=User,
    objects=users,
    save=users_repo.save,
    delete=users_repo.delete,
    exclude=("id", "superadmin"),
    can_edit=lambda user: not user.superadmin,
    can_delete=lambda user: not user.superadmin,
)


with st.expander("Użytkownicy", expanded=True):
    st.button("Odśwież")
    st.dataframe(users, column_config=user_column_config_mapping)


new_user = render_add_form(
    users_crud,
    key="user_add",
    title="Dodaj użytkownika",
)
if new_user:
    with execute_with_toast(f"Użytkownik '{new_user.email}' dodany!"):
        users_repo.save(new_user)
    st.rerun()


edited_user = render_edit_form(
    users_crud,
    key="user_edit",
    title="Edytuj użytkownika",
    select_label="Wybierz użytkownika",
)
if edited_user:
    with execute_with_toast(f"Użytkownik '{edited_user.email}' zedytowany!"):
        users_repo.save(edited_user)
    st.rerun()


deleted_users = render_delete_form(
    users_crud,
    key="user_delete",
    title="Usuń użytkownika",
    select_label="Wybierz użytkownika/użytkowników",
)
if deleted_users:
    for user_to_delete in deleted_users:
        with execute_with_toast(f"Użytkownik '{user_to_delete.email}' usunięty!"):
            users_repo.delete(user_to_delete)
    st.rerun()
