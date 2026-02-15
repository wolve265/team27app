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

    def __init__(self) -> None:
        if self.NAME in st.session_state:
            notifications: list[Notification] = st.session_state.pop(self.NAME)
            for notification in notifications:
                st.toast(notification.msg, icon=notification.icon)

        if self.NAME not in st.session_state:
            st.session_state[self.NAME] = list()
            return

    def add(self, msg: str, icon: str|None=None) -> None:
        st.session_state[self.NAME].append(Notification(msg, icon))
