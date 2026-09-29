from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import streamlit as st
from pydantic import BaseModel, ValidationError

from utils.streamlit.pydantic import FieldRenderer, pydantic_input


@dataclass(frozen=True)
class CrudSpec[ModelT: BaseModel]:
    model: type[ModelT]
    objects: Sequence[ModelT]
    save: Callable[[ModelT], Any]
    delete: Callable[[ModelT], Any]
    format_func: Callable[[ModelT], str] = str
    add_values: Mapping[str, Any] | None = None
    field_renderers: Mapping[str, FieldRenderer[Any, Any]] | None = None
    exclude: Sequence[str] = ("id",)
    can_edit: Callable[[ModelT], bool] = lambda _obj: True
    can_delete: Callable[[ModelT], bool] = lambda _obj: True


def render_add_form[ModelT: BaseModel](
    spec: CrudSpec[ModelT],
    *,
    key: str,
    title: str,
    submit_label: str = "Dodaj",
) -> ModelT | None:
    with st.form(key):
        st.subheader(title, text_alignment="center")
        data = pydantic_input(
            spec.model,
            key=f"{key}_fields",
            values=spec.add_values,
            field_renderers=spec.field_renderers,
            exclude=spec.exclude,
        )
        if not st.form_submit_button(submit_label):
            return None
        return _validate_model(spec.model, data)


def render_edit_form[ModelT: BaseModel](
    spec: CrudSpec[ModelT],
    *,
    key: str,
    title: str,
    select_label: str = "Wybierz element",
    submit_label: str = "Zapisz",
) -> ModelT | None:
    objects = list(spec.objects)
    with st.container(border=True):
        st.subheader(title, text_alignment="center")
        selected = st.selectbox(
            select_label,
            index=None,
            options=objects,
            format_func=spec.format_func,
            key=f"{key}_selected",
            on_change=lambda: _sync_selected_model(spec, key),
        )
        if selected is None:
            return None
        if not spec.can_edit(selected):
            st.warning("Nie możesz edytować tego elementu.")
            return None

        with st.form(f"{key}_form"):
            data = pydantic_input(
                spec.model,
                key=f"{key}_fields",
                values=selected.model_dump(),
                field_renderers=spec.field_renderers,
                exclude=spec.exclude,
            )
            if not st.form_submit_button(submit_label):
                return None

    data.update({name: getattr(selected, name) for name in spec.exclude})
    return _validate_model(spec.model, data)


def render_delete_form[ModelT: BaseModel](
    spec: CrudSpec[ModelT],
    *,
    key: str,
    title: str,
    select_label: str = "Wybierz element",
    submit_label: str = "Usuń",
) -> list[ModelT] | None:
    deletable_objects = [obj for obj in spec.objects if spec.can_delete(obj)]
    with st.container(border=True):
        st.subheader(title, text_alignment="center")
        selected = st.multiselect(
            select_label,
            options=deletable_objects,
            format_func=spec.format_func,
            key=f"{key}_selected",
        )
        if selected and st.button(submit_label, key=f"{key}_submit"):
            return selected
    return None


def _sync_selected_model[ModelT: BaseModel](spec: CrudSpec[ModelT], key: str) -> None:
    selected = st.session_state.get(f"{key}_selected")
    if selected is None:
        return

    for field_name in spec.model.model_fields:
        if field_name in spec.exclude:
            continue
        st.session_state[f"{key}_fields_{field_name}"] = getattr(selected, field_name)


def _validate_model[ModelT: BaseModel](
    model: type[ModelT], data: Mapping[str, Any]
) -> ModelT | None:
    try:
        return model.model_validate(data)
    except ValidationError as error:
        st.error(f"Nieprawidłowe dane:\n\n{error}")
        return None
