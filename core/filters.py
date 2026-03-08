import streamlit as st
from .globals import (
    GENERATOR_COLUMNS,
    BINYAN_ORDER,
    MODE_ORDER,
    PERSON_ORDER,
    GENDER_ORDER,
    NUMBER_ORDER,
)

# ==========================================================
# Configuration
# ==========================================================

POLEL_DATASETS = {
    "II-Yod Vav (קום)",
    "II-Geminate (סבב)",
}

ORDER_MAP = {
    "Mode": MODE_ORDER,
    "Person": PERSON_ORDER,
    "Gender": GENDER_ORDER,
    "Number": NUMBER_ORDER,
}


# ==========================================================
# Binyan Logic
# ==========================================================

def get_binyan_options(df):
    """
    Return the appropriate Binyan order depending on the datasets loaded.
    """

    active_datasets = set(df["Dataset"].unique())

    has_polel = bool(active_datasets & POLEL_DATASETS)
    only_polel = active_datasets and active_datasets.issubset(POLEL_DATASETS)

    if only_polel:
        order = [
            "Qal",
            "Niphal",
            "Polel",
            "Polal",
            "Hitpolel",
            "Hiphil",
            "Hophal",
        ]

    elif has_polel:
        order = [
            "Qal",
            "Niphal",
            "Piel",
            "Polel",
            "Pual",
            "Polal",
            "Hitpael",
            "Hitpolel",
            "Hiphil",
            "Hophal",
        ]

    else:
        order = BINYAN_ORDER

    raw = [str(x).strip() for x in df["Binyan"].dropna().unique().tolist()]

    return [o for o in order if o in raw]


# ==========================================================
# Option Ordering
# ==========================================================

def ordered_options_from_df(df, column):

    if column not in df.columns:
        return []

    if column == "Binyan":
        return get_binyan_options(df)

    opts_raw = [str(x).strip() for x in df[column].dropna().unique().tolist()]

    if column in ORDER_MAP:
        return [o for o in ORDER_MAP[column] if o in opts_raw]

    return opts_raw


# ==========================================================
# Filter State Management
# ==========================================================

def reset_filters(prefix: str):
    for col in GENERATOR_COLUMNS:
        key = f"{prefix}_{col}"
        if key in st.session_state:
            del st.session_state[key]


# ==========================================================
# Sidebar Filter Rendering
# ==========================================================

def render_sidebar_filters(prefix: str, df, disabled: bool = False):

    selections = {}

    st.sidebar.markdown("### Filters")

    if st.sidebar.button("Reset Filters", disabled=disabled):
        reset_filters(prefix)
        st.rerun()

    for col in GENERATOR_COLUMNS:

        key = f"{prefix}_{col}"
        opts = ordered_options_from_df(df, col)

        if key not in st.session_state:
            st.session_state[key] = []

        # Remove invalid selections if dataset changes
        st.session_state[key] = [v for v in st.session_state[key] if v in opts]

        selections[col] = st.sidebar.multiselect(
            col,
            options=opts,
            key=key,
            disabled=disabled,
        )

    return selections
