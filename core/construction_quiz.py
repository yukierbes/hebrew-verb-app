# ==================================================
# Imports
# ==================================================

from io import BytesIO
import pandas as pd
import streamlit as st

from core.helpers import get_filtered_rows, is_valid_combo
from core.tables import show_clean_table
from core.session import reset_quiz_state

# ==================================================
# Constants
# ==================================================

MORPH_COLUMNS = ["Binyan", "Mode", "Person", "Gender", "Number"]


# ==================================================
# Reset Quiz
# ==================================================
def reset_construction_quiz_state():
    st.session_state.construction_quiz_step = "filters"
    st.session_state.construction_use_filters = True
    st.session_state.construction_quiz_df = None
    st.session_state.construction_quiz_questions = []
    st.session_state.construction_quiz_results = []
    st.session_state.construction_quiz_index = 0
    st.session_state.quiz_active = False

    for key in list(st.session_state.keys()):
        if key.startswith("revealed_"):
            del st.session_state[key]


# ==================================================
# Run Quiz Entry
# ==================================================
def run_construction_quiz(df, filters):
    if "construction_quiz_step" not in st.session_state:
        reset_construction_quiz_state()

    step = st.session_state.construction_quiz_step

    if step == "filters":
        step_filters(df, filters)
        return

    # Initialize quiz DF once after filters
    if st.session_state.construction_quiz_df is None:
        working = df.copy()
        if st.session_state.construction_use_filters:
            working = get_filtered_rows(working, st.session_state.locked_filters)

        if working.empty:
            st.warning("⚠️ No verbs match the selected filters. Adjust your filters.")
            return  # Do not proceed until filters produce results

        grouped = (
            working.groupby(MORPH_COLUMNS + ["Dataset"], dropna=False)
            .agg({"Conjugation": list, "Gloss Translation": list})
            .reset_index()
        )
        st.session_state.construction_quiz_df = grouped

    # Step routing
    if step == "length":
        step_length()
    elif step == "question":
        step_question()
    elif step == "summary":
        step_summary()

# ==================================================
# Step 1 — Filter Choice
# ==================================================

def step_filters(df, filters):

    st.subheader("Construction Quiz")
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

            st.session_state.construction_use_filters = True
            st.session_state.locked_filters = locked_filters
            st.session_state.quiz_active = True
            st.session_state.construction_quiz_step = "length"
            st.rerun()

    with c2:
        if st.button("No, use all verbs", use_container_width=True):
            st.session_state.construction_use_filters = False
            st.session_state.locked_filters = st.session_state.get("current_filters", {})
            st.session_state.quiz_active = True
            st.session_state.construction_quiz_step = "length"
            st.rerun()


# ==================================================
# Step 2 — Quiz Length
# ==================================================

def step_length():

    df = st.session_state.construction_quiz_df

    st.subheader("How many questions?")

    n = st.number_input(
        "Questions",
        min_value=1,
        max_value=len(df),
        value=min(10, len(df)),
    )

    if st.button("Start Quiz", use_container_width=True):

        st.session_state.construction_quiz_questions = (
            df.sample(n).to_dict("records")
        )

        st.session_state.construction_quiz_index = 0
        st.session_state.construction_quiz_results = []
        st.session_state.construction_quiz_step = "question"

        st.rerun()


# ==================================================
# Step 3 — Questions
# ==================================================

def step_question():
    idx = st.session_state.construction_quiz_index
    qs = st.session_state.construction_quiz_questions
    total = len(qs)

    if idx >= total:
        st.session_state.construction_quiz_step = "summary"
        st.rerun()

    q = qs[idx]

    st.progress((idx + 1) / total)
    st.caption(f"Question {idx + 1} of {total}")

    row_data = {k: q[k] for k in MORPH_COLUMNS if q.get(k)}
    if "Dataset" in q and str(q["Dataset"]).strip():
        row_data["Dataset"] = q["Dataset"]
    show_clean_table(pd.DataFrame([row_data]))

    if f"revealed_{idx}" not in st.session_state:
        if st.button("Reveal Answer", use_container_width=True):
            st.session_state[f"revealed_{idx}"] = True
            st.rerun()
        return

    forms = q["Conjugation"]
    glosses = q["Gloss Translation"]

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

    c1, c2, c3 = st.columns([1.25,1.25,0.5])

    with c1:
        if st.button("I got it right", use_container_width=True):
            record(q, "Correct")
            advance()
    with c2:
        if st.button("I got it wrong", use_container_width=True):
            record(q, "Incorrect")
            advance()
    with c3:
        if st.button("End Quiz", use_container_width=True):
            for rem_idx in range(idx, total):
                q_rem = qs[rem_idx]
                record(q_rem, "NA")
            st.session_state.construction_quiz_index = total
            st.session_state.construction_quiz_step = "summary"
            st.rerun()
    
# ==================================================
# Step 4 — Summary
# ==================================================

def step_summary():
    st.header("Quiz Summary")

    df = pd.DataFrame(st.session_state.construction_quiz_results)
    total = len(df)
    correct = (df["Result"] == "Correct").sum()
    percent = round((correct / total) * 100) if total else 0

    st.subheader(f"Score: {correct} / {total} ({percent}%)")
    st.write("---")

    # Highlight results
    def format_result(val):
        if val == "Correct":
            return "<span style='background:#E7F6E7;padding:4px 8px;border-radius:6px;font-weight:600;'>{}</span>".format(val)
        elif val == "NA":
            return "<span style='background:#FFF4D6;padding:4px 8px;border-radius:6px;font-weight:600;'>{}</span>".format(val)
        else:
            return "<span style='background:#FFE6E6;padding:4px 8px;border-radius:6px;font-weight:600;'>{}</span>".format(val)

    df["Result"] = df["Result"].apply(format_result)
    show_clean_table(df)

    # -----------------------
    # Downloads
    # -----------------------
    csv = df.to_csv(index=False).encode("utf-8")
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Download CSV", csv, "construction_quiz_results.csv", "text/csv", use_container_width=True)
    with c2:
        st.download_button("Download Excel", excel_buffer.getvalue(), "construction_quiz_results.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    st.write("---")
    if st.button("Quiz Again", use_container_width=True):
        reset_construction_quiz_state()
        st.rerun()


# ==================================================
# Helpers
# ==================================================

def record(q, result):

    st.session_state.construction_quiz_results.append({
        **{k: q[k] for k in MORPH_COLUMNS},
        "Dataset": q.get("Dataset", ""),
        "Correct Answers": " / ".join(q["Conjugation"]),
        "Result": result,
    })


def advance():

    st.session_state.construction_quiz_index += 1
    st.rerun()

