# ==================================================
# Imports
# ==================================================

import pandas as pd
import streamlit as st

from core.construction_quiz import run_construction_quiz
from core.datasets import render_dataset_selector
from core.filters import render_sidebar_filters
from core.globals import set_background, inject_global_hebrew_font, inject_global_styles
from core.helpers import get_filtered_rows, is_valid_combo
from core.session import reset_quiz_state
from core.sidebar import show_sidebar_navigation
from core.tables import show_clean_table


# ==================================================
# Constants
# ==================================================

DISPLAY_COLUMNS = ["Binyan", "Mode", "Person", "Gender", "Number"]
MORPH_COLUMNS = ["Binyan", "Mode", "Person", "Gender", "Number"]


# ==================================================
# Helpers
# ==================================================

def build_display_table(row):

    data = {
        col: row[col]
        for col in DISPLAY_COLUMNS
        if col in row and str(row[col]).strip() not in ("", "nan")
    }

    if "Dataset" in row and str(row["Dataset"]).strip():
        data["Dataset"] = row["Dataset"]

    return pd.DataFrame([data])


# ==================================================
# Practice Mode
# ==================================================

def show_practice(df, filters):

    st.subheader("Verb Construction Practice")

    st.markdown(
        """
        <div style="background:var(--secondary-background-color);
            padding:16px;
            border-radius:12px;
            border:2px solid var(--primary-color);
            color:var(--text-color);
            margin-bottom:10px;
        ">
        <b>Instructions</b><br>
        Click <i>Generate a Verb</i>, construct the form, then reveal all valid answers.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("---")

    # ==================================================
    # Generate Verb
    # ==================================================

    if st.button("Generate a Verb", use_container_width=True):

        valid = df[df.apply(is_valid_combo, axis=1)]
        valid = get_filtered_rows(valid, filters)

        if valid.empty:
            st.warning("No verbs match the selected filters.")
            return

        grouped = (
            valid
            .groupby(MORPH_COLUMNS + ["Dataset"], dropna=False)
            .agg({
                "Conjugation": list,
                "Gloss Translation": list,
            })
            .reset_index()
        )

        st.session_state.construction_verb = grouped.sample(1).iloc[0].to_dict()
        st.session_state.construction_show_answer = False

        st.rerun()

    verb = st.session_state.get("construction_verb")

    if not verb:
        return

    # ==================================================
    # Display Verb Features
    # ==================================================

    st.write("---")
    show_clean_table(build_display_table(verb))

    # ==================================================
    # Show Answer
    # ==================================================

    st.write("---")

    if st.button("Show Answer", use_container_width=True):
        st.session_state.construction_show_answer = True

    if st.session_state.get("construction_show_answer"):

        forms = verb.get("Conjugation", [])
        glosses = verb.get("Gloss Translation", [])

        for i, form in enumerate(forms):

            gloss = glosses[i] if i < len(glosses) else ""

            st.markdown(
                f"""
                <div style="text-align:center;">
                    <span lang="he" dir="rtl"
                          style="font-family:'SBL Hebrew', serif;
                                 font-size:100px;">
                        {form}
                    </span>
                    <br/>
                    <span style="font-size:22px;">
                        {gloss}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==================================================
# Page Controller
# ==================================================

def page():

    # ------------------------------------------------
    # Reset quiz whenever user enters this page
    # ------------------------------------------------
    if st.session_state.get("last_page") != "construction":
        reset_quiz_state()
        st.session_state.last_page = "construction"

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

    st.title("Verb Construction")
    st.write("---")

    mode = st.radio(
        "Mode",
        ["Practice", "Quiz"],
        horizontal=True,
        key="construction_mode",
    )

    # ==================================================
    # Sidebar Filters
    # ==================================================

    if not st.session_state.get("quiz_active", False):
        filters = render_sidebar_filters("construction", df)
        st.session_state.current_filters = filters
    else:
        filters = st.session_state.get("locked_filters", {})

    st.write("---")

    # ==================================================
    # Mode Routing
    # ==================================================

    if mode == "Practice":
        show_practice(df, filters)
    else:
        run_construction_quiz(df, filters)

    # ==================================================
    # Navigation
    # ==================================================

    st.write("---")

    # Show "Return to Home" only in Practice or at the Summary step
    if mode == "Practice" or (
        mode == "Quiz"
        and st.session_state.get("construction_quiz_step") == "summary"
    ):
        if st.button("Return to Home Page"):
            reset_quiz_state()
            st.session_state.page = "home"
            st.rerun()
