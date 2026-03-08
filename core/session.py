import streamlit as st
from .globals import GENERATOR_COLUMNS


# ==========================================================
# Quiz Default State
# ==========================================================

DEFAULTS_QUIZ = {
    "quiz_active": False,
    "quiz_stage": "idle",
    "quiz_use_filters": True,
    "quiz_length": 0,
    "quiz_questions": [],
    "quiz_index": 0,
    "quiz_responses": [],
    "quiz_user_answers": [],
    "quiz_started_from_sidebar_filters": {},
    "quiz_started_at": None,
    "quiz_title": "",
}


# ==========================================================
# Session Initialization
# ==========================================================

def initialize_session_state():

    if "page" not in st.session_state:
        st.session_state.page = "home"

    if "filter_presets" not in st.session_state:
        st.session_state.filter_presets = {}

    if "table_view_mode" not in st.session_state:
        st.session_state.table_view_mode = "expanded"

    if "visible_review_columns" not in st.session_state:
        st.session_state.visible_review_columns = GENERATOR_COLUMNS.copy()

    if "review_filters" not in st.session_state:
        st.session_state.review_filters = {c: [] for c in GENERATOR_COLUMNS}

    for k, v in DEFAULTS_QUIZ.items():
        st.session_state.setdefault(k, v)


# ==========================================================
# Quiz Reset
# ==========================================================

def reset_quiz_state():

    # ------------------------------
    # Reset global quiz state
    # ------------------------------
    for k in DEFAULTS_QUIZ:
        st.session_state.pop(k, None)

    # ------------------------------
    # Reset identification quiz
    # ------------------------------
    ident_keys = [
        "ident_quiz_step",
        "ident_use_filters",
        "ident_quiz_df",
        "ident_quiz_questions",
        "ident_quiz_results",
        "ident_quiz_index",
        "ident_quiz_input_mode",
    ]

    for k in ident_keys:
        st.session_state.pop(k, None)

    for k in list(st.session_state.keys()):
        if k.startswith("q_"):
            del st.session_state[k]

    # ------------------------------
    # Reset construction quiz
    # ------------------------------
    construction_keys = [
        "construction_quiz_step",
        "construction_use_filters",
        "construction_quiz_df",
        "construction_quiz_questions",
        "construction_quiz_results",
        "construction_quiz_index",
    ]

    for k in construction_keys:
        st.session_state.pop(k, None)

    for k in list(st.session_state.keys()):
        if k.startswith("revealed_"):
            del st.session_state[k]
