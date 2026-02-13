from typing import Any

import pymongo
import streamlit as st
from pymongo.database import Database


@st.cache_resource
def get_client() -> pymongo.MongoClient[Any]:
    """Initialize connection.

    Uses `st.cache_resource` to only run once.
    """
    return pymongo.MongoClient(**st.secrets["mongo"])


@st.cache_resource
def get_db(db_name="t27app") -> Database:
    return get_client()[db_name]
