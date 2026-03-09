# ==================================================
# Imports
# ==================================================

from io import BytesIO

import pandas as pd
import streamlit as st

from core.datasets import render_dataset_selector
from core.filters import render_sidebar_filters
from core.globals import set_background
from core.sidebar import show_sidebar_navigation
from core.tables import show_clean_table


# ==================================================
# Page
# ==================================================

def page():

    # ==================================================
    # Setup
    # ==================================================

    set_background("other")
    show_sidebar_navigation()

    st.title("Verb Review")

    st.markdown(
        """
        <div style="background:var(--secondary-background-color);
            padding:16px;
            border-radius:12px;
            border:2px solid var(--primary-color);
            color:var(--text-color);
            margin-bottom:10px;
        ">
        💡 <strong>Tip:</strong> Use the filters in the sidebar to narrow the table.<br>
        Download the table to create flashcards or study lists.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ==================================================
    # Dataset Selection
    # ==================================================

    df = render_dataset_selector()
    if df is None or df.empty:
        return

    st.sidebar.markdown("---")

    if df.empty:
        st.warning("No data found for selected datasets.")
        return

    # ==================================================
    # Sidebar Filters
    # ==================================================

    filters = render_sidebar_filters("review", df)

    for col, vals in filters.items():
        if vals:
            df = df[df[col].isin(vals)]

    # ==================================================
    # No Results Warning
    # ==================================================

    if df.empty:
        st.warning("No verbs match the selected filters.")
        return

    # ==================================================
    # Column Visibility
    # ==================================================

    st.sidebar.markdown("---")
    st.sidebar.subheader("Visible Columns")

    if (
        "visible_review_columns" not in st.session_state
        or set(st.session_state.visible_review_columns) != set(df.columns)
    ):
        st.session_state.visible_review_columns = list(df.columns)

    visible_cols = st.sidebar.multiselect(
        "Show columns",
        options=list(df.columns),
        default=st.session_state.visible_review_columns,
    )

    st.session_state.visible_review_columns = visible_cols or list(df.columns)

    visible_df = df[st.session_state.visible_review_columns]

    # ==================================================
    # Table Display
    # ==================================================

    st.markdown("<div class='center-container'>", unsafe_allow_html=True)
    show_clean_table(visible_df)
    st.markdown("</div>", unsafe_allow_html=True)

    # ==================================================
    # Downloads
    # ==================================================

    st.markdown("---")
    st.markdown("### Download Data")

    csv_data = visible_df.to_csv(index=False).encode("utf-8")

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        visible_df.to_excel(writer, index=False, sheet_name="Verbs")

    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "Download CSV",
            csv_data,
            "verbs_filtered.csv",
            "text/csv",
            use_container_width=True,
        )

    with c2:
        st.download_button(
            "Download Excel",
            excel_buffer.getvalue(),
            "verbs_filtered.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # ==================================================
    # Navigation
    # ==================================================

    st.markdown("---")

    if st.button("Return to Home Page"):
        st.session_state.page = "home"
        st.rerun()
