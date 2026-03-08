import sys
from pathlib import Path
import streamlit as st

# Ensure parent directory is on the Python path
sys.path.append(str(Path(__file__).resolve().parent))

st.set_page_config(
    page_title="Biblical Hebrew Verb Practice",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Now safe to import the rest ---
from core.session import initialize_session_state
from core.globals import inject_global_styles
import custom_pages.home as home
import custom_pages.construction as construction
import custom_pages.identification as identification
import custom_pages.review as review
from core.globals import inject_global_hebrew_font

# --- Initialize session state ---
inject_global_styles()
initialize_session_state()
inject_global_hebrew_font()

# --- Page routing dictionary ---
PAGES = {
    "home": home.page,
    "construction": construction.page,
    "identification": identification.page,
    "review": review.page,
}

# --- Run selected page ---
current = st.session_state.get("page", "home")
page_fn = PAGES.get(current, home.page)
page_fn()
