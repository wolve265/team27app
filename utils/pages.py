from contextlib import contextmanager
from dataclasses import dataclass

import streamlit as st
from streamlit.commands.page_config import Layout

APP_NAME = "Team27App"


def set_page(page_name: str, *, layout: Layout = "centered") -> None:
    st.set_page_config(
        page_title=f"{page_name} - {APP_NAME}",
        page_icon="⚽",
        layout=layout,
    )
    st.header(page_name, divider=True, text_alignment="center")


@dataclass
class Notification:
    msg: str
    icon: str | None = None


class ToastNotifications:
    NAME = "toast_notifications"

    @staticmethod
    def render() -> None:
        if ToastNotifications.NAME in st.session_state:
            notifications: list[Notification] = st.session_state.pop(ToastNotifications.NAME)
            for notification in notifications:
                st.toast(notification.msg, icon=notification.icon)

        if ToastNotifications.NAME not in st.session_state:
            st.session_state[ToastNotifications.NAME] = list()
            return

    @staticmethod
    def add(msg: str, icon: str | None = None) -> None:
        st.session_state[ToastNotifications.NAME].append(Notification(msg, icon))


@contextmanager
def execute_with_toast(
    success_msg: str,
    error_icon: str = "❌",
    success_icon: str = "✅",
):
    """Context manager for executing code with automatic toast notifications.

    Args:
        success_msg: Message to show on success
        error_icon: Icon for error notifications (default: ❌)
        success_icon: Icon for success notifications (default: ✅)

    Usage:
        with execute_with_toast("Operation succeeded!"):
            repo.save(item)
        st.rerun()
    """
    try:
        yield
    except Exception as e:
        ToastNotifications.add(msg=str(e), icon=error_icon)
    else:
        ToastNotifications.add(msg=success_msg, icon=success_icon)
