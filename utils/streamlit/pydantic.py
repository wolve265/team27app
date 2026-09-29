import datetime as dt
from collections.abc import Mapping, Sequence
from enum import Enum
from types import UnionType
from typing import Any, Protocol, Union, cast, get_args, get_origin

import streamlit as st
from pydantic import BaseModel, EmailStr
from pydantic.fields import FieldInfo


class FieldRenderer[InputT, OutputT](Protocol):
    """Render a custom widget from a field value into the model's value type."""

    def __call__(
        self,
        field_name: str,
        widget_key: str,
        field: FieldInfo,
        value: InputT,
    ) -> OutputT: ...


def pydantic_input(
    model: type[BaseModel],
    key: str,
    *,
    values: Mapping[str, Any] | None = None,
    field_renderers: Mapping[str, FieldRenderer[Any, Any]] | None = None,
    exclude: Sequence[str] = ("id",),
) -> dict[str, Any]:
    """Render basic Streamlit inputs from a Pydantic model's fields.

    Relationships and other specialized fields can be supplied through
    ``field_renderers``. The returned values still need model validation by
    constructing ``model(**data)``.
    """
    values = values or {}
    field_renderers = field_renderers or {}
    data: dict[str, Any] = {}

    for name, field in model.model_fields.items():
        value = values.get(name, _default_value(field, data))
        if name in exclude:
            data[name] = value
            continue

        field_key = f"{key}_{name}"
        if renderer := field_renderers.get(name):
            data[name] = renderer(name, field_key, field, value)
            continue

        data[name] = _render_field(name, field_key, field, value)

    return data


def _default_value(field: FieldInfo, values: dict[str, Any]) -> Any:
    if field.is_required():
        return None
    return field.get_default(call_default_factory=True, validated_data=values)


def _constraint(field: FieldInfo, name: str) -> Any:
    return next(
        (
            value
            for metadata in field.metadata
            if (value := getattr(metadata, name, None)) is not None
        ),
        None,
    )


def _render_field(name: str, key: str, field: FieldInfo, value: Any) -> Any:
    annotation = field.annotation
    origin = get_origin(annotation)
    args = get_args(annotation)
    optional = False
    if origin in (UnionType, Union):
        non_none_args = tuple(arg for arg in args if arg is not type(None))
        optional = len(non_none_args) != len(args)
        if len(non_none_args) == 1:
            annotation = non_none_args[0]

    label = field.title or name.replace("_", " ").capitalize()
    description = field.description

    if annotation in (str, EmailStr):
        kwargs: dict[str, Any] = {"key": key, "help": description}
        if max_length := _constraint(field, "max_length"):
            kwargs["max_chars"] = max_length
        return st.text_input(label, value=value or "", **kwargs).strip()

    if annotation is bool:
        return st.checkbox(label, value=bool(value), key=key, help=description)

    if annotation in (int, float):
        kwargs = {"key": key, "help": description}
        for constraint, widget_arg in (
            ("ge", "min_value"),
            ("gt", "min_value"),
            ("le", "max_value"),
            ("lt", "max_value"),
            ("multiple_of", "step"),
        ):
            constraint_value = _constraint(field, constraint)
            if constraint_value is not None and widget_arg not in kwargs:
                kwargs[widget_arg] = constraint_value
        return cast(Any, st.number_input)(label, value=value, **kwargs)

    if annotation is dt.datetime:
        initial = value if isinstance(value, dt.datetime) else None
        selected_date = st.date_input(
            label,
            value=initial.date() if initial else dt.datetime.now(tz=dt.UTC).date(),
            key=f"{key}_date",
            help=description,
        )
        selected_time = st.time_input(
            f"{label} - godzina",
            value=initial.time().replace(tzinfo=None) if initial else dt.time(),
            key=f"{key}_time",
        )
        return dt.datetime.combine(selected_date, selected_time).replace(
            tzinfo=initial.tzinfo if initial else None
        )

    if annotation is dt.date:
        return st.date_input(
            label,
            value=(value if isinstance(value, dt.date) else dt.datetime.now(tz=dt.UTC).date()),
            key=key,
            help=description,
        )

    if isinstance(annotation, type) and issubclass(annotation, Enum):
        options: list[Enum | None] = list(annotation)
        if optional:
            options.insert(0, None)
        selected_index = options.index(value) if value in options else 0
        return st.selectbox(
            label,
            options=options,
            index=selected_index,
            key=key,
            help=description,
            format_func=lambda option: "" if option is None else str(option),
        )

    raise TypeError(
        f"Unsupported field type for '{name}': {annotation!r}. Provide a custom field renderer."
    )
