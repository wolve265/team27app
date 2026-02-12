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
