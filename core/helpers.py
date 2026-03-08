import pandas as pd


# ==========================================================
# Validation Helpers
# ==========================================================

def is_valid_combo(row):
    """Return True if the row has a valid conjugation."""
    return str(row.get("Conjugation", "")).strip() != ""


# ==========================================================
# Data Filtering
# ==========================================================

def get_filtered_rows(df: pd.DataFrame, filters: dict):
    """
    Filter a dataframe using selected filter values.
    """
    data = df.copy()

    for col, vals in filters.items():
        if vals:
            data = data[data[col].isin(vals)]

    return data


# ==========================================================
# Conjugation Grouping
# ==========================================================

def group_by_conjugation(df: pd.DataFrame, preserve_cols=None) -> pd.DataFrame:
    """
    Group rows by morphological features and return one
    conjugation per combination.
    """

    morph_columns = ["Binyan", "Mode", "Person", "Gender", "Number"]

    df = df.dropna(subset=["Conjugation"])

    group_cols = morph_columns.copy()

    if preserve_cols:
        group_cols += [c for c in preserve_cols if c not in group_cols]

    grouped = df.groupby(group_cols, dropna=False, as_index=False).first()

    return grouped.reset_index(drop=True)


# ==========================================================
# Answer Normalization
# ==========================================================

def normalize_answer(value):
    """Convert scalar or list-like answers into a display-safe string."""

    if value is None:
        return ""

    if isinstance(value, (list, tuple, set)):
        return " / ".join(map(str, value))

    return str(value)


# ==========================================================
# Binyan Detection
# ==========================================================

def get_available_binyanim(df):

    base = ["Qal", "Niphal", "Piel", "Pual", "Hitpael", "Hiphil", "Hophal"]

    polel_sets = {
        "II-Yod Vav (קום)",
        "II-Geminate (סבב)",
    }

    active_datasets = set(df["Dataset"].unique())

    if active_datasets.intersection(polel_sets):
        return ["Qal", "Niphal", "Polel", "Polal", "Hitpolel", "Hiphil", "Hophal"]

    return base
