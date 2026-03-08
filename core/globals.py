import streamlit as st
import pandas as pd
from pathlib import Path


# ==========================================================
# Global Constants
# ==========================================================

GENERATOR_COLUMNS = ["Binyan", "Mode", "Person", "Gender", "Number"]

BINYAN_ORDER = ["Qal", "Niphal", "Piel", "Pual", "Hitpael", "Hiphil", "Hophal"]

MODE_ORDER = [
    "Perfect", "Imperfect", "Jussive", "Cohortative", "Imperative",
    "Infinitive Absolute", "Infinitive Construct",
    "Active Participle", "Passive Participle",
]

PERSON_ORDER = ["3", "2", "1"]
GENDER_ORDER = ["M", "F", "C"]
NUMBER_ORDER = ["S", "P"]


# ==========================================================
# Data Loading
# ==========================================================

@st.cache_data
def load_answers(path: str = "Answers.xlsx"):
    """Load Answers.xlsx and perform basic normalization."""
    p = Path(path)

    if not p.exists():
        st.error(
            f"Answers file not found at {path}. "
            "Place Answers.xlsx in the app root or update the path."
        )
        return pd.DataFrame()

    df = pd.read_excel(p)

    # Remove unnamed columns and fill NaN
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")].fillna("")

    # Normalize Person column
    if "Person" in df.columns:

        def _norm_person(x):
            if x == "":
                return ""
            try:
                f = float(x)
                return str(int(f)) if f.is_integer() else str(x)
            except Exception:
                return str(x)

        df["Person"] = df["Person"].apply(_norm_person)

    # Normalize text columns
    for col in ["Mode", "Binyan", "Gender", "Number", "Conjugation"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Remove Status column if present
    if "Status" in df.columns:
        df = df.drop(columns=["Status"])

    return df


# ==========================================================
# Global Styling
# ==========================================================

def inject_global_styles():
    st.markdown(
        """
        <style>
        :root { --primary-color: #AA4BFF; }

        div.stSidebar div.stButton>button {
            background-color: var(--primary-color) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            font-weight: 600 !important;
            width: calc(100% - 16px) !important;
            display: block !important;
            margin: 0 auto 8px auto;
            font-size: 1rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
            transition: all 0.2s ease-in-out;
        }

        div.stSidebar div.stButton>button:hover {
            background-color: #922CFF !important;
            transform: translateY(-2px);
        }

        div.stButton>button {
            background-color: var(--primary-color) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            font-weight: 600 !important;
        }

        div.stButton>button:hover {
            background-color: #922CFF !important;
        }

        .custom-table th {
            background: #F5F0FF;
            color: #7A2CFF;
            padding: 8px;
            text-align: center;
        }

        .custom-table td {
            padding: 6px;
            text-align: center;
            border-bottom: 1px solid #E0CCFF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_global_hebrew_font():
    st.markdown(
        """
        <link rel="stylesheet"
              href="https://fonts.googleapis.com/css2?family=SBL+Hebrew&display=swap">

        <style>
        span[lang="he"],
        div[lang="he"],
        p[lang="he"],
        .dataframe td,
        .dataframe th {
            font-family: 'SBL Hebrew', serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# Page Background Styling
# ==========================================================

def set_background(page: str = "home"):

    if page == "home":
        st.markdown(
            """
            <style>
            [data-testid="stAppViewContainer"],
            section[data-testid="stSidebar"] {
                background: linear-gradient(135deg, #F5F0FF 0%, #E6D6FF 100%) !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    else:
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"] {
                background: linear-gradient(135deg, #F5F0FF 0%, #E6D6FF 100%) !important;
            }

            [data-testid="stAppViewContainer"] {
                background-color: white !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
