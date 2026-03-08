import streamlit as st
import random
from .session import reset_quiz_state


# ==========================================================
# Quiz Question Pool
# ==========================================================

def prepare_quiz_pool(answers_df, filters_snapshot, use_filters, n, validate_fn):

    pool = answers_df.copy()

    if use_filters and filters_snapshot:
        for col, vals in filters_snapshot.items():
            if vals and col in pool.columns:
                pool = pool[pool[col].isin(vals)]

    if validate_fn is not None:
        pool = pool[pool.apply(validate_fn, axis=1)]

    if pool.empty:
        pool = answers_df[answers_df.apply(validate_fn, axis=1)]

    if pool.empty:
        return []

    if len(pool) >= n:
        return pool.sample(n, replace=False).to_dict("records")

    base = pool.sample(len(pool), replace=False).to_dict("records")
    remainder = n - len(base)
    extra = pool.sample(remainder, replace=True).to_dict("records")

    return base + extra


# ==========================================================
# Quiz Controller
# ==========================================================

def simple_quiz_controller(
    answers_df,
    filters_snapshot,
    validate_fn,
    question_renderer,
    result_builder,
    title="Quiz",
):

    # ----------------------------
    # Start Quiz
    # ----------------------------

    if not st.session_state.get("quiz_active", False):

        if st.button("Start Quiz", use_container_width=True):
            st.session_state.quiz_active = True
            st.session_state.quiz_stage = "confirm_filters"
            st.session_state.quiz_started_from_sidebar_filters = filters_snapshot.copy()
            st.rerun()

    # ----------------------------
    # Confirm Filter Usage
    # ----------------------------

    if (
        st.session_state.get("quiz_active")
        and st.session_state.get("quiz_stage") == "confirm_filters"
    ):

        st.subheader("Start Quiz")

        choice = st.radio(
            "Do you want to quiz with current filter selections?",
            ("Yes", "No"),
            index=0,
        )

        st.session_state.quiz_use_filters = choice == "Yes"

        cols = st.columns([5, 1])

        with cols[0]:
            if st.button("Continue", use_container_width=True):
                st.session_state.quiz_stage = "choose_length"
                st.rerun()

        with cols[1]:
            if st.button("Cancel", use_container_width=True):
                reset_quiz_state()
                st.rerun()

        st.stop()

    
