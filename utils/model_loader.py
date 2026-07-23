import os
import joblib
import streamlit as st

MODEL_PATH = "models/random_forest.pkl"
SCALER_PATH = "models/scaler.pkl"


@st.cache_resource
def load_model():
    """
    Load the trained Random Forest model.
    This is cached so the model is loaded only once.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found:\n{MODEL_PATH}")

    return joblib.load(MODEL_PATH)


@st.cache_resource
def load_scaler():
    """
    Load the StandardScaler.
    This is cached so the scaler is loaded only once.
    """
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(f"Scaler file not found:\n{SCALER_PATH}")

    return joblib.load(SCALER_PATH)