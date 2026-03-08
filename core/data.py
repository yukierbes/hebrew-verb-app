# core/data.py

import pandas as pd
from functools import lru_cache

DATA_FILE = "data/Answers.xlsx"

# ==========================================================
# Configuration
# ==========================================================

# Columns that exist in Excel but should never reach the UI
REFERENCE_COLUMNS = {
    "Status",
}


# ==========================================================
# Dataset Discovery
# ==========================================================

def get_available_datasets() -> list[str]:
    """
    Return all available dataset names (Excel sheet tabs).
    """
    try:
        return pd.ExcelFile(DATA_FILE).sheet_names
    except FileNotFoundError:
        return []


# ==========================================================
# Verb Data Loading
# ==========================================================

@lru_cache(maxsize=None)
def load_verb_data(selected_datasets: tuple[str, ...]) -> pd.DataFrame:
    """
    Load and concatenate verb data from selected Excel sheets.
    """
    frames: list[pd.DataFrame] = []

    for sheet_name in selected_datasets:
        try:
            df = pd.read_excel(DATA_FILE, sheet_name=sheet_name)
        except ValueError:
            continue

        # ----------------------------
        # Data Normalization
        # ----------------------------

        df = df.drop(columns=df.columns.intersection(REFERENCE_COLUMNS))
        df = df.fillna("")

        if "Person" in df.columns:
            df["Person"] = df["Person"].apply(
                lambda x: str(int(x))
                if isinstance(x, (int, float)) and str(x).strip() != ""
                else str(x)
            )

        for col in ("Gender", "Number"):
            if col in df.columns:
                df[col] = df[col].astype(str)

        # Track dataset provenance
        df["Dataset"] = sheet_name

        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
