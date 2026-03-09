import streamlit as st
import pandas as pd

# ==========================================================
# Styled Table Rendering
# ==========================================================

def show_clean_table(df, compact=None, columns=None, width="80%"):
    """
    Display a DataFrame with unified styling, centered on the page,
    and horizontally scrollable if needed.

    Args:
        df: DataFrame to display
        compact: use compact spacing
        columns: optional list of columns to display
        width: CSS width of the table container
    """

    if df is None or df.empty:
        st.info("No data available.")
        return

    # ----------------------------
    # Data Cleaning
    # ----------------------------
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")].reset_index(drop=True)

    if columns:
        df = df[[c for c in columns if c in df.columns]]

    compact = compact or (st.session_state.get("table_view_mode") == "compact")
    cls = "compact-table" if compact else "expanded-table"

    # ----------------------------
    # Table Styling
    # ----------------------------
    st.markdown(
        f"""
        <style>
        .custom-table {{
            border-collapse: collapse;
            width: {width};
            margin: 1rem auto;
            font-family: 'Segoe UI', sans-serif;
            font-size: 1.5rem;
            color: var(--text-color);
        }}

        .custom-table th {{
            background: var(--secondary-background-color);
            color: var(--primary-color);
            border-bottom: 2px solid var(--secondary-background-color);
            text-align: center;
            padding: 8px;
            white-space: nowrap;
        }}

        .custom-table td {{
            border-bottom: 1px solid var(--secondary-background-color);
            text-align: center;
            padding: 6px;
            color: var(--text-color);
        }}

        .custom-table tr:nth-child(even) {{
            background-color: var(--background-color);
        }}

        .custom-table tr:hover {{
            background-color: var(--secondary-background-color);
        }}

        .compact-table td,
        .compact-table th {{
            padding: 4px;
            font-size: 0.9rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ----------------------------
    # Table Rendering (Scrollable)
    # ----------------------------
    st.markdown(
        f"""
        <div style="overflow-x:auto;">
            {df.to_html(index=False, escape=False, classes=f"custom-table {cls}")}
        </div>
        """,
        unsafe_allow_html=True,
    )
