from types import SimpleNamespace

import pytest

from team27app.utils.db.users import User, UserRole
from team27app.utils.streamlit import crud, pydantic
from team27app.utils.streamlit.crud import (
    CrudSpec,
    render_add_form,
    render_delete_form,
    render_edit_form,
)


class FormContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def user_spec(users: list[User]) -> CrudSpec[User]:
    return CrudSpec(
        model=User,
        objects=users,
        save=lambda user: None,
        delete=lambda user: None,
        format_func=lambda user: user.email,
        exclude=("id", "superadmin"),
        can_edit=lambda user: not user.superadmin,
        can_delete=lambda user: not user.superadmin,
    )


def test_render_add_form_builds_validated_model(monkeypatch: pytest.MonkeyPatch):
    widgets = SimpleNamespace(
        text_input=lambda _label, **_kwargs: "admin@example.com",
        selectbox=lambda _label, **_kwargs: UserRole.ADMIN,
        checkbox=lambda _label, **_kwargs: False,
    )
    monkeypatch.setattr(pydantic, "st", widgets)
    monkeypatch.setattr(crud.st, "form", lambda _key: FormContext())
    monkeypatch.setattr(crud.st, "subheader", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(crud.st, "form_submit_button", lambda _label: True)

    result = render_add_form(
        user_spec([]),
        key="user_add",
        title="Dodaj użytkownika",
    )

    assert result == User(email="admin@example.com", role=UserRole.ADMIN)


def test_edit_selection_uses_fresh_field_keys_on_every_change(
    monkeypatch: pytest.MonkeyPatch,
):
    users = [
        User(email="first@example.com", role=UserRole.ADMIN),
        User(email="second@example.com", role=UserRole.ADMIN),
    ]
    spec = user_spec(users)
    state = {}
    field_keys = []

    monkeypatch.setattr(crud.st, "session_state", state)
    monkeypatch.setattr(crud.st, "container", lambda **_kwargs: FormContext())
    monkeypatch.setattr(crud.st, "form", lambda *_args, **_kwargs: FormContext())
    monkeypatch.setattr(crud.st, "subheader", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(crud.st, "form_submit_button", lambda _label: False)

    def select_user(_label, **kwargs):
        kwargs["on_change"]()
        return users.pop(0)

    monkeypatch.setattr(crud.st, "selectbox", select_user)
    monkeypatch.setattr(
        crud,
        "pydantic_input",
        lambda _model, *, key, **_kwargs: field_keys.append(key) or {},
    )

    render_edit_form(spec, key="user_edit", title="Edytuj użytkownika")
    render_edit_form(spec, key="user_edit", title="Edytuj użytkownika")

    assert field_keys == ["user_edit_fields_1", "user_edit_fields_2"]


def test_render_delete_form_excludes_protected_objects(monkeypatch: pytest.MonkeyPatch):
    admin = User(email="admin@example.com", role=UserRole.ADMIN)
    superadmin = User(email="root@example.com", role=UserRole.ADMIN, superadmin=True)
    monkeypatch.setattr(crud.st, "container", lambda **_kwargs: FormContext())
    monkeypatch.setattr(crud.st, "subheader", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(crud.st, "multiselect", lambda *_args, **_kwargs: [admin])
    monkeypatch.setattr(crud.st, "button", lambda *_args, **_kwargs: True)

    result = render_delete_form(
        user_spec([admin, superadmin]),
        key="user_delete",
        title="Usuń użytkownika",
    )

    assert result is not None
    assert result == [admin]
    assert superadmin not in result
