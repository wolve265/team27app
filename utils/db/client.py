from typing import Any

import pymongo
import streamlit as st


@st.cache_resource
def get_client() -> pymongo.MongoClient[Any]:
    """Initialize connection.

    Uses `st.cache_resource` to only run once.
    """
    return pymongo.MongoClient(**st.secrets["mongo"])
