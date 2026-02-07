import streamlit as st

from menu import menu_with_redirect
from utils.db.users import (
    User,
    UserRole,
    add_user,
    delete_user,
    edit_user_role,
    get_all_users,
)

menu_with_redirect(roles=[UserRole.ADMIN, UserRole.SUPERADMIN])

st.header("Manage Users")

def refresh_users() -> None:
    st.session_state.users = get_all_users()

if "users" not in st.session_state:
    refresh_users()

users: list[User] = st.session_state.users

with st.expander("All users", expanded=True):
    st.button("Refresh users", on_click=refresh_users, help="Use this button after every operation to see the updated users list.")
    st.table(users)


with st.form("Add user", clear_on_submit=True):
    st.header("Add user", text_alignment="center")
    email = st.text_input("Email")
    role = st.selectbox("Role", UserRole.list_all())
    submit = st.form_submit_button()
    if submit:
        if not email:
            st.error("Email is required!")
        else:
            user = User(email=email, role=UserRole(role))
            try:
                add_user(user)
            except Exception as e:
                st.error(str(e))
            else:
                st.success(f"User '{email}' with role '{role}' added!")

with st.container(border=True):
    st.header("Edit user role", text_alignment="center")
    email = st.selectbox("Select user to edit role", options=[u["email"] for u in users])
    user = next(u for u in users if u["email"] == email)
    is_superadmin = user["role"] == UserRole.SUPERADMIN
    if is_superadmin:
        st.warning("Cannot edit role of a superadmin user!")
    else:
        user_role_index = UserRole.list_all().index(user["role"])
        role = st.selectbox("Role", options=UserRole.list_all(), index=user_role_index, disabled=is_superadmin)
    submit = st.button("Edit user", disabled=is_superadmin)
    if submit:
        try:
            edit_user_role(email, UserRole(role))
        except Exception as e:
            st.error(str(e))
        else:
            st.success(f"User '{email}' role changed to '{role}'!")

with st.container(border=True):
    st.header("Delete user", text_alignment="center")
    email = st.selectbox("Select user to delete", options=[u["email"] for u in users])
    user = next(u for u in users if u["email"] == email)
    is_superadmin = user["role"] == UserRole.SUPERADMIN
    if is_superadmin:
        st.warning("Cannot delete a superadmin user!")
    submit = st.button("Delete user", disabled=is_superadmin)
    if submit:
        try:
            delete_user(email)
        except Exception as e:
            st.error(str(e))
        else:
            st.success(f"User '{email}' deleted!")
