# ==================================================
# Imports
# ==================================================
from io import BytesIO
import pandas as pd
import streamlit as st

from core.filters import ordered_options_from_df
from core.helpers import get_filtered_rows, group_by_conjugation
from core.tables import show_clean_table

FIELDS = ["Binyan", "Stem", "Person", "Gender", "Number"]
FIELD_MAP = {"Stem": "Mode"}


# ==================================================
# Reset Quiz
# ==================================================
def reset_ident_quiz_state():
    st.session_state.ident_quiz_step = "filters"
    st.session_state.ident_use_filters = True
    st.session_state.ident_quiz_df = None
    st.session_state.ident_quiz_questions = []
    st.session_state.ident_quiz_results = []
    st.session_state.ident_quiz_index = 0
    st.session_state.ident_quiz_input_mode = "Dropdown"
    st.session_state.quiz_active = False

    # Clear previous input keys
    for key in list(st.session_state.keys()):
        if key.startswith("q_"):
            del st.session_state[key]


# ==================================================
# Run Quiz Entry
# ==================================================
def run_identification_quiz(df, filters):
    """
    Main controller for the Identification Quiz.
    Always reset at first entry if not in a valid step.
    """
    if (
        "ident_quiz_step" not in st.session_state
        or st.session_state.ident_quiz_step not in ["filters", "length", "input_mode", "question", "summary"]
    ):
        reset_ident_quiz_state()

    step = st.session_state.ident_quiz_step

    if step == "filters":
        step_filters(df, filters)
        return

    # Initialize quiz DF once after filters
    if st.session_state.ident_quiz_df is None:
        working = df.copy()
        if st.session_state.ident_use_filters:
            working = get_filtered_rows(working, st.session_state.locked_filters)

        if working.empty:
            st.warning("⚠️ No verbs match the selected filters. Adjust your filters.")
            return  # Do not proceed until filters produce results

        preserve_cols = ["Dataset"] if "Dataset" in working.columns else []
        grouped = group_by_conjugation(working, preserve_cols=preserve_cols)

        for col in ["Conjugation", "Gloss Translation"]:
            grouped[col] = grouped[col].apply(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x)

        st.session_state.ident_quiz_df = grouped.reset_index(drop=True)

    # Step routing
    if step == "length":
        step_length()
    elif step == "input_mode":
        step_input_mode()
    elif step == "question":
        step_question()
    elif step == "summary":
        step_summary()


# ==================================================
# Step 1 — Filter Choice
# ==================================================
def step_filters(df, filters):
    st.subheader("Identification Quiz")
    st.write("Do you want to use the current sidebar filters for this quiz?")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Yes, use filters", use_container_width=True):

            locked_filters = st.session_state.get("current_filters", {})
            working = df.copy()
            working = get_filtered_rows(working, locked_filters)

            if working.empty:
                st.warning("No verbs match the selected filters. Please adjust the filters before starting the quiz.")
                return

            st.session_state.ident_use_filters = True
            st.session_state.locked_filters = locked_filters
            st.session_state.quiz_active = True
            st.session_state.ident_quiz_step = "length"
            st.rerun()

    with c2:
        if st.button("No, use all verbs", use_container_width=True):
            st.session_state.ident_use_filters = False
            st.session_state.locked_filters = st.session_state.get("current_filters", {})
            st.session_state.quiz_active = True
            st.session_state.ident_quiz_step = "length"
            st.rerun()
            
# ==================================================
# Step 2 — Quiz Length
# ==================================================

def step_length():

    df = st.session_state.ident_quiz_df

    st.subheader("How many questions?")

    n = st.number_input(
        "Questions",
        min_value=1,
        max_value=len(df),
        value=min(10, len(df)),
    )

    if st.button("Continue", use_container_width=True):

        if "Dataset" in df.columns:

            datasets = df["Dataset"].unique()
            per_dataset = max(1, n // len(datasets))

            samples = []

            for ds in datasets:
                ds_rows = df[df["Dataset"] == ds]
                k = min(per_dataset, len(ds_rows))
                samples.append(ds_rows.sample(k))

            quiz_df = pd.concat(samples)

            if len(quiz_df) < n:
                remaining = df.drop(quiz_df.index)
                extra = remaining.sample(min(n - len(quiz_df), len(remaining)))
                quiz_df = pd.concat([quiz_df, extra])

            quiz_df = quiz_df.sample(n).reset_index(drop=True)

        else:
            quiz_df = df.sample(n).reset_index(drop=True)

        st.session_state.ident_quiz_questions = quiz_df.to_dict("records")
        st.session_state.ident_quiz_index = 0
        st.session_state.ident_quiz_step = "input_mode"

        st.rerun()


# ==================================================
# Step 3 — Input Mode
# ==================================================

def step_input_mode():

    st.subheader("Answer Input Mode")

    st.session_state.ident_quiz_input_mode = st.radio(
        "Choose how you want to answer:",
        ["Dropdown", "Typing", "Selection"],
        horizontal=True,
    )

    if st.button("Start Quiz", use_container_width=True):
        st.session_state.ident_quiz_step = "question"
        st.rerun()


# ==================================================
# Step 4 — Questions
# ==================================================

def step_question():

    idx = st.session_state.ident_quiz_index
    qs = st.session_state.ident_quiz_questions
    total = len(qs)

    if idx >= total:
        st.session_state.ident_quiz_step = "summary"
        st.rerun()

    row = qs[idx]

    st.progress((idx + 1) / total)
    st.caption(f"Question {idx + 1} of {total}")

    forms = row["Conjugation"]

    st.markdown(
        f"""
        <div style="text-align:center;">
            <span lang="he" dir="rtl"
                  style="font-family:'SBL Hebrew', serif;font-size:100px;">
                {forms}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------
    # User Inputs
    # ------------------------------------------------

    user_answers = {}

    def ordered(col):

        if col == "Binyan":
            df_quiz = st.session_state.ident_quiz_df
            if df_quiz is not None and "Dataset" in df_quiz.columns:
                return ordered_options_from_df(df_quiz, "Binyan")
            return ["Qal", "Niphal", "Piel", "Pual", "Hitpael", "Hiphil", "Hophal"]

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

    for field in FIELDS:

        col = FIELD_MAP.get(field, field)

        st.markdown(
            f"<div style='padding:8px;border-radius:10px;border:1px solid #E2D6FF;font-weight:600;'>{field}</div>",
            unsafe_allow_html=True,
        )

        mode = st.session_state.ident_quiz_input_mode

        if mode == "Dropdown":
            user_answers[field] = st.selectbox(
                "",
                [""] + ordered(col),
                key=f"q_{idx}_{field}",
            )

        elif mode == "Typing":
            user_answers[field] = st.text_input(
                "",
                key=f"q_{idx}_{field}",
            )

        else:
            user_answers[field] = st.radio(
                "",
                ordered(col),
                key=f"q_{idx}_{field}",
                horizontal=True,
            )

    # ------------------------------------------------
    # Next Question & End Quiz Buttons
    # ------------------------------------------------

    cols = st.columns([4, 1])  # Wide column for Next, narrow for End Quiz

    with cols[0]:
        if st.button("Next Question", use_container_width=True):
            record_answer(row, user_answers)
            st.session_state.ident_quiz_index += 1
            st.rerun()

    with cols[1]:
        if st.button("End Quiz",use_container_width=True):
            # Fill unanswered questions with NA
            idx = st.session_state.ident_quiz_index
            qs = st.session_state.ident_quiz_questions

            for i in range(idx, len(qs)):
                question = qs[i]
                empty_answers = {f: "NA" for f in FIELDS}
                record_answer(question, empty_answers)

            # Jump to summary
            st.session_state.ident_quiz_step = "summary"
            st.rerun()


# ==================================================
# Step 5 — Summary
# ==================================================

def color_answer(user, valid):

    normalized_user = "" if user == "NA" else user

    if not user:
        return ""

    if normalized_user in valid:
        return f"<span style='background:rgba(40,167,69,0.25);padding:3px 8px;border-radius:6px;font-weight:600;'>{user}</span>"

    return f"<span style='background:rgba(220,53,69,0.25);padding:3px 8px;border-radius:6px;font-weight:600;'>{user}</span>"


def step_summary():

    st.header("Quiz Summary")

    df = pd.DataFrame(st.session_state.ident_quiz_results)

    total_points = len(df) * len(FIELDS)
    earned = df["Score"].sum()
    percent = round((earned / total_points) * 100)

    st.subheader(f"Score: {earned} / {total_points} ({percent}%)")
    st.write("---")

    display_df = df.copy()

    if "Conjugation" in display_df.columns:
        cols = display_df.columns.tolist()
        cols.insert(1, cols.pop(cols.index("Conjugation")))
        display_df = display_df[cols]

    for field in FIELDS:
        display_df[f"Your {field}"] = display_df.apply(
            lambda r: color_answer(r[f"Your {field}"], r[field].split(" / ")),
            axis=1,
        )

    show_clean_table(display_df)

    csv = df.to_csv(index=False).encode("utf-8")

    excel_buffer = BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    st.write("---")

    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "Download CSV",
            csv,
            "identification_quiz_results.csv",
            "text/csv",
            use_container_width=True,
        )

    with c2:
        st.download_button(
            "Download Excel",
            excel_buffer.getvalue(),
            "identification_quiz_results.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.write("---")

    if st.button("Quiz Again", use_container_width=True):
        reset_ident_quiz_state()
        st.rerun()

    st.write("---")

    if st.button("Return to Home"):
        reset_ident_quiz_state()
        st.session_state.page = "home"
        st.rerun()


# ==================================================
# Helpers
# ==================================================

def record_answer(row, user_answers):

    score = 0

    result = {
        "Question": len(st.session_state.ident_quiz_results) + 1,
        "Conjugation": row["Conjugation"],
    }

    for field in FIELDS:

        col = FIELD_MAP.get(field, field)
        valid = row[col]
        user = user_answers.get(field, "")

        if isinstance(valid, str):
            valid = [valid]

        if user == "NA":
            user = ""

        result[field] = " / ".join(valid)
        result[f"Your {field}"] = user if user != "" else "NA"

        if user in valid:
            score += 1

    result["Score"] = score

    st.session_state.ident_quiz_results.append(result)


# ==================================================
# Reset
# ==================================================

def reset_ident_quiz_state():

    st.session_state.ident_quiz_step = "filters"
    st.session_state.ident_use_filters = True
    st.session_state.ident_quiz_df = None
    st.session_state.ident_quiz_questions = []
    st.session_state.ident_quiz_results = []
    st.session_state.ident_quiz_index = 0
    st.session_state.ident_quiz_input_mode = "Dropdown"

    st.session_state.quiz_active = False

    for key in list(st.session_state.keys()):
        if key.startswith("q_"):
            del st.session_state[key]
