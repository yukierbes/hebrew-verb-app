# ==================================================
# Imports
# ==================================================

import pandas as pd
import streamlit as st

from core.datasets import render_dataset_selector
from core.filters import render_sidebar_filters, ordered_options_from_df
from core.globals import set_background, inject_global_styles, inject_global_hebrew_font
from core.helpers import group_by_conjugation
from core.identification_quiz import run_identification_quiz
from core.session import reset_quiz_state
from core.sidebar import show_sidebar_navigation
from core.tables import show_clean_table


# ==================================================
# Constants
# ==================================================

FIELDS = ["Binyan", "Mode", "Person", "Gender", "Number"]
FIELD_MAP = {}


# ==================================================
# Session State Initialization
# ==================================================

def init_identification_state():
    defaults = {
        "ident_row": None,
        "ident_checked": False,
        "ident_show_answer": False,
        "ident_input_mode": "Dropdown",
        "ident_user_answers": {},
    }

    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


# ==================================================
# Practice Mode
# ==================================================

def show_practice(df, filters):

    st.subheader("Verb Parsing Practice")

    st.markdown(
        """
        <div style="
            background:var(--secondary-background-color);
            padding:16px;
            border-radius:12px;
            border:2px solid var(--primary-color);
            color:var(--text-color);
            margin-bottom:10px;
        ">
        <b>Instructions</b><br>
        Click <i>Generate a Verb</i> to generate a random conjugation. Then parse the features of the verb.<br>
        Click <i>Check Answer</i> for feedback or <i>Show Answer</i> to reveal the solution/s.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("---")

    # ==================================================
    # Apply Filters
    # ==================================================

    working = df.copy()

    for col, selected in filters.items():
        if selected:
            working = working[working[col].isin(selected)]

    preserve_cols = ["Dataset"] if "Dataset" in working.columns else []
    grouped = group_by_conjugation(working, preserve_cols=preserve_cols)

    st.session_state.ident_input_mode = st.radio(
        "Answer Input Mode", ["Dropdown", "Typing", "Selection"], horizontal=True
    )

    st.write("---")

    # ==================================================
    # Generate Verb
    # ==================================================

    if st.button("Generate Verb", use_container_width=True):

        if grouped.empty:
            st.warning("No verbs match the selected filters.")
            return

        selected_datasets = filters.get("Dataset", [])

        if selected_datasets:
            sample_rows = []

            for ds in selected_datasets:
                ds_rows = grouped[grouped["Dataset"] == ds]

                if not ds_rows.empty:
                    sample_rows.append(ds_rows.sample(1).iloc[0])

            row = pd.DataFrame(sample_rows).sample(1).iloc[0]
        else:
            row = grouped.sample(1).iloc[0]

        st.session_state.ident_row = row
        st.session_state.ident_checked = False
        st.session_state.ident_show_answer = False
        st.session_state.ident_user_answers = {}

        st.rerun()

    row = st.session_state.ident_row

    if row is None:
        st.info("Click **Generate Verb** to begin.")
        return

    # ==================================================
    # Display Verb
    # ==================================================

    forms = row["Conjugation"]

    if isinstance(forms, list) and len(forms) == 1:
        forms = forms[0]

    st.markdown(
        f"""
        <div style="text-align:center;">
            <span lang="he" dir="rtl" style="font-family:'SBL Hebrew', serif;font-size:100px;">
                {forms}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_answers = st.session_state.ident_user_answers

    # ==================================================
    # Feedback Header Coloring
    # ==================================================

    def header_color(label):

        if not st.session_state.ident_checked:
            return "var(--secondary-background-color)"

        user = user_answers.get(label, "")
        valid = row[FIELD_MAP.get(label, label)]

        if isinstance(valid, str):
            valid = [valid]

        normalized_user = "" if user == "NA" else user

        if normalized_user in valid:
            return "rgba(40,167,69,0.25)"

        if user:
            return "rgba(255,193,7,0.30)"

        return "var(--secondary-background-color)"
        
    # ==================================================
    # Dropdown / Input Options
    # ==================================================

    def ordered_options(col):

        if col == "Binyan":
            return ordered_options_from_df(df, "Binyan")

        if col == "Mode":
            return [
                "Perfect",
                "Imperfect",
                "Jussive",
                "Cohortative",
                "Imperative",
                "Infinitive Absolute",
                "Infinitive Construct",
                "Active Participle",
                "Passive Participle",
            ]

        if col == "Person":
            return ["3", "2", "1", "NA"]

        if col == "Gender":
            return ["M", "F", "C", "NA"]

        if col == "Number":
            return ["S", "P", "NA"]

        return []

    # ==================================================
    # Input Fields
    # ==================================================

    for label in FIELDS:

        col_name = FIELD_MAP.get(label, label)

        st.markdown(
            f"""
            <div style="
                padding:8px 12px;
                border-radius:10px;
                border:1px solid #E2D6FF;
                background:{header_color(label)};
                font-weight:600;
            ">
                {label}
            </div>
            """,
            unsafe_allow_html=True,
        )
        mode = st.session_state.ident_input_mode

        if mode == "Dropdown":
            user_answers[label] = st.selectbox(
                "", [""] + ordered_options(col_name), key=f"ident_{label}"
            )

        elif mode == "Typing":
            user_answers[label] = st.text_input("", key=f"ident_{label}")

        else:
            user_answers[label] = st.radio(
                "",
                ordered_options(col_name),
                key=f"ident_sel_{label}",
                horizontal=True,
            )

    # ==================================================
    # Action Buttons
    # ==================================================

    st.write("---")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Check Answer", use_container_width=True):
            st.session_state.ident_checked = True

    with c2:
        if st.button("Show Answer", use_container_width=True):
            st.session_state.ident_show_answer = True

    # ==================================================
    # Answer Table
    # ==================================================

    if st.session_state.ident_show_answer:

        row_conjugation = row["Conjugation"]

        if not isinstance(row_conjugation, list):
            row_conjugation = [row_conjugation]

        matching_rows = df[df["Conjugation"].isin(row_conjugation)]
        answer_df = matching_rows[FIELDS].copy()

        show_centered = st.columns([1, 3, 1])

        with show_centered[1]:
            show_clean_table(answer_df)


# ==================================================
# Page Controller
# ==================================================

def page():

    # ------------------------------------------------
    # Reset quiz whenever user enters this page
    # ------------------------------------------------
    if st.session_state.get("last_page") != "identification":
        reset_quiz_state()
        st.session_state.last_page = "identification"

    set_background("other")
    show_sidebar_navigation()
    inject_global_hebrew_font()
    inject_global_styles()

    # ==================================================
    # Dataset Selection
    # ==================================================

    # ----------------------------------------------
    # Dataset selector (hide during quiz)
    # ----------------------------------------------

    if not st.session_state.get("quiz_active", False):
        df = render_dataset_selector()
    else:
        df = st.session_state.get("locked_dataset_df")

    if df is None or df.empty:
        return

    # Save dataset snapshot when quiz starts
    if not st.session_state.get("quiz_active", False):
        st.session_state.locked_dataset_df = df

    st.sidebar.markdown("---")

    st.title("Verb Parsing")
    st.write("---")

    init_identification_state()

    mode = st.radio("Mode", ["Practice", "Quiz"], horizontal=True)
    st.write("---")

       

    # ----------------------------------------------
    # Sidebar Filters
    # ----------------------------------------------

    if not st.session_state.get("quiz_active", False):
        filters = render_sidebar_filters("identification", df)
        st.session_state.current_filters = filters
    else:
        filters = st.session_state.get("locked_filters", {})

    # ----------------------------------------------
    # Mode Routing
    # ----------------------------------------------

    if mode == "Quiz":
        run_identification_quiz(df, filters)
        return

    show_practice(df, filters)

    st.write("---")

    if st.button("Return to Home Page"):
        reset_quiz_state()
        st.session_state.page = "home"
        st.rerun()
