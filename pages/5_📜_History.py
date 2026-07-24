import streamlit as st
import pandas as pd

from config import setup_page, load_css
from utils.auth_guard import require_login
from utils.ai_assistant import render_ai_assistant
from database.history import get_user_history

setup_page()
load_css()

require_login()
render_ai_assistant("history")

st.title("📜 Prediction History")

username = st.session_state.username

history = get_user_history(username)

if not history:
    st.info("No prediction history available.")
    st.stop()

df = pd.DataFrame([dict(row) for row in history])

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download History CSV",
    csv,
    file_name="prediction_history.csv",
    mime="text/csv",
)
