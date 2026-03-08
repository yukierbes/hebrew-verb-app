import streamlit as st
from .data import get_available_datasets, load_verb_data


# ==========================================================
# Dataset Selector (Shared Across Pages)
# ==========================================================

def render_dataset_selector():
    """
    Render the dataset selector in the sidebar and return
    a DataFrame containing the selected datasets.
    """

    st.sidebar.markdown("### Datasets")

    available = get_available_datasets()

    if not available:
        st.error("No datasets found in Answers.xlsx.")
        return None

    # ----------------------------
    # Session State Initialization
    # ----------------------------

    if "selected_datasets" not in st.session_state:
        st.session_state.selected_datasets = [available[0]]

    # ----------------------------
    # State Sanitization
    # ----------------------------

    st.session_state.selected_datasets = [
        d for d in st.session_state.selected_datasets if d in available
    ]

    # ----------------------------
    # Dataset Selection UI
    # ----------------------------

    selected = st.sidebar.multiselect(
        "Select datasets",
        options=available,
        key="selected_datasets",
    )

    if not selected:
        st.warning("Select at least one dataset.")
        return None

    # ----------------------------
    # Load Selected Data
    # ----------------------------

    return load_verb_data(tuple(selected))
