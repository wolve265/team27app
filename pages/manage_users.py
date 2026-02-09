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

users: list[User] = get_all_users()
for u in users:
    keys_to_pop = [key for key in u.keys() if key.startswith("_")]
    for key in keys_to_pop:
        u.pop(key)  # type: ignore

if "notification" in st.session_state:
    notification = st.session_state.pop("notification")
    icon = notification["icon"]
    st.toast(notification["msg"], icon=icon)

st.header("Zarządzanie użytkownikami")

with st.expander("Użytkownicy", expanded=True):
    st.button("Odśwież")
    st.table(users)

with st.form("add_user_form"):
    st.header("Dodaj użytkownika", text_alignment="center")
    email = st.text_input("Email")
    role = st.selectbox("Rola", UserRole.list_all())
    submit = st.form_submit_button("Dodaj")
    if submit:
        if not email:
            st.error("Email jest wymagany!")
        else:
            user = User(email=email, role=UserRole(role))
            try:
                add_user(user)
            except Exception as e:
                st.session_state.notification = {"icon": "❌", "msg": str(e)}
            else:
                st.session_state.notification = {
                    "icon": "✅",
                    "msg": f"Użytkownik '{email}' o roli '{role}' dodany!",
                }
            finally:
                st.rerun()

with st.container(border=True):
    st.header("Edytuj rolę użytkownika", text_alignment="center")
    email = st.selectbox(
        "Wybierz użytkownika", key="edit_user", options=[u["email"] for u in users]
    )
    user = next(u for u in users if u["email"] == email)
    is_superadmin = user["role"] == UserRole.SUPERADMIN
    if is_superadmin:
        st.warning(f"Nie możesz edytować użytkownika o roli '{UserRole.SUPERADMIN}'!")
    else:
        user_role_index = UserRole.list_all().index(user["role"])
        role = st.selectbox(
            "Rola",
            options=UserRole.list_all(),
            index=user_role_index,
            disabled=is_superadmin,
        )
    submit = st.button("Edytuj rolę", disabled=is_superadmin)
    if submit:
        try:
            edit_user_role(email, UserRole(role))
        except Exception as e:
            st.session_state.notification = {"icon": "❌", "msg": str(e)}
        else:
            st.session_state.notification = {
                "icon": "✅",
                "msg": f"Rola użytkownika '{email}' zmieniona na '{role}'!",
            }
        finally:
            st.rerun()

with st.container(border=True):
    st.header("Usuń użytkownika", text_alignment="center")
    email = st.selectbox(
        "Wybierz użytkownika", key="delete_user", options=[u["email"] for u in users]
    )
    user = next(u for u in users if u["email"] == email)
    is_superadmin = user["role"] == UserRole.SUPERADMIN
    if is_superadmin:
        st.warning(f"Nie możesz usunąć użytkownika o roli '{UserRole.SUPERADMIN}'!")
    submit = st.button("Usuń", disabled=is_superadmin)
    if submit:
        try:
            delete_user(email)
        except Exception as e:
            st.session_state.notification = {"icon": "❌", "msg": str(e)}
        else:
            st.session_state.notification = {
                "icon": "✅",
                "msg": f"User '{email}' deleted!",
            }
        finally:
            st.rerun()
