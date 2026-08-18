import streamlit as st

from config import load_css, setup_page
from utils.ai_assistant import render_ai_assistant, render_ai_workspace
from utils.auth_guard import require_login


setup_page()
load_css()
require_login()
render_ai_assistant("assistant")

render_ai_workspace()
