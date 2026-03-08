import streamlit as st


# ==========================================================
# Sidebar Navigation
# ==========================================================

def show_sidebar_navigation():

    # Inject CSS for full-width navigation buttons
    st.markdown(
        """
        <style>
        div.stButton > button {
            width: 100% !important;
            border-radius: 8px;
            margin-bottom: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:

        with st.expander("Navigation", expanded=True):

            from core.session import reset_quiz_state

            if st.button("Home", key="nav_home"):
                reset_quiz_state()
                st.session_state.page = "home"
                st.rerun()

            if st.button("Verb Review", key="nav_review"):
                reset_quiz_state()
                st.session_state.page = "review"
                st.rerun()

            if st.button("Verb Parsing", key="nav_identification"):
                reset_quiz_state()
                st.session_state.page = "identification"
                st.rerun()

            if st.button("Verb Construction", key="nav_construction"):
                reset_quiz_state()
                st.session_state.page = "construction"
                st.rerun()

        
