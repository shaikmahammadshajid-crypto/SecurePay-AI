import os
from functools import lru_cache

import joblib


MODEL_PATH = "models/random_forest.pkl"
SCALER_PATH = "models/scaler.pkl"


@lru_cache(maxsize=1)
def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {e}")


@lru_cache(maxsize=1)
def load_scaler():
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(f"Scaler file not found: {SCALER_PATH}")

    try:
        return joblib.load(SCALER_PATH)
    except Exception as e:
        raise RuntimeError(f"Failed to load scaler: {e}")
