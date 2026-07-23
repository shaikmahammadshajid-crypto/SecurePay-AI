import streamlit as st


def setup_page():
    """Configure the Streamlit page."""

    st.set_page_config(
        page_title="SecurePay AI",
        page_icon="💳",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def load_css():
    """Load the custom CSS stylesheet."""

    try:
        with open("assets/style.css", "r", encoding="utf-8") as css:
            st.markdown(
                f"<style>{css.read()}</style>",
                unsafe_allow_html=True,
            )
    except FileNotFoundError:
        st.warning("⚠️ assets/style.css not found.")
    except Exception as e:
        st.error(f"Unable to load CSS: {e}")