# ==================================================
# Imports
# ==================================================

import streamlit as st

from core.globals import set_background, inject_global_styles
from core.sidebar import show_sidebar_navigation


# ==================================================
# Page
# ==================================================

def page():

    # ==================================================
    # Setup
    # ==================================================

    set_background("home")
    inject_global_styles()
    show_sidebar_navigation()

    st.title("Biblical Hebrew Verb Practice")
    st.write("How would you like to study?")

    st.markdown(
        "<style>div.block-container{padding-top:1rem;max-width:2000px;}</style>",
        unsafe_allow_html=True,
    )

    # ==================================================
    # Study Modes
    # ==================================================

    sidebar_labels = {
        "review": "Verb Review",
        "identification": "Verb Parsing",
        "construction": "Verb Construction",
    }

    study_modes = [
        {
            "label": "Review",
            "desc": "Study verb forms by browsing and filtering the verbs",
            "key": "review",
        },
        {
            "label": "Parsing",
            "desc": "Parse verbs from the generated conjugations",
            "key": "identification",
        },
        {
            "label": "Construction",
            "desc": "Master verb morphology by being able to write it",
            "key": "construction",
        },
    ]

    cols = st.columns(3, gap="large")

    for col, mode in zip(cols, study_modes):

        with col:

            st.markdown(
                f"""
                <div style='
                    background:white;
                    border-radius:20px;
                    border:1px solid #E2D6FF;
                    box-shadow:0 2px 8px rgba(0,0,0,0.1);
                    padding:32px 24px;
                    height:220px;
                    display:flex;
                    flex-direction:column;
                    align-items:center;
                    justify-content:center;
                    text-align:center;
                    transition:all 0.2s ease-in-out;
                '
                onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)';"
                onmouseout="this.style.transform='none'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)';">
                    <div style='display:flex; flex-direction:column; justify-content:center; height:100%;'>
                        <h2 style='color:#AA4BFF; margin:0 0 1rem 0;'>{mode["label"]}</h2>
                        <p style='color:#555; margin:0; font-size:0.95rem; line-height:1.4;'>{mode["desc"]}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

            button_label = sidebar_labels[mode["key"]]

            if st.button(
                button_label,
                key=f"home_{mode['key']}",
                use_container_width=True,
            ):
                st.session_state.page = mode["key"]
                st.rerun()

    # ==================================================
    # Footer Verse
    # ==================================================

    st.markdown("<div style='height:7rem'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <link rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=SBL+Hebrew&display=swap">

        <div style="
            text-align: center;
            direction: rtl;
            font-size: 2.75rem;
            color: black;
            font-family: 'SBL Hebrew', serif;
            line-height: 2.4rem;
        ">
            וְאָהַבְתָּ אֵת יְהוָה אֱלֹהֶיךָ בְּכָל-לְבָבְךָ
            וּבְכָל-נַפְשְׁךָ וּבְכָל-מְאֹדֶךָ
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ==================================================
    # Feedback
    # ==================================================

    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:0.95rem;
            color:#555;
        ">
            <b>Found a mistake or have a suggestion?</b><br>
            Help improve the Hebrew Verb App by reporting issues or submitting feedback.<br><br>
            <a href="https://forms.gle/abrMxJfCp6mpLH9y6" target="_blank"
               style="
               background:#AA4BFF;
               color:white;
               padding:0.5rem 1.2rem;
               border-radius:8px;
               text-decoration:none;
               font-weight:600;">
               Submit Feedback
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
