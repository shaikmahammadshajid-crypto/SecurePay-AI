from __future__ import annotations

from datetime import datetime, timezone
import uuid

import numpy as np
import pandas as pd

from config import FEATURE_COLUMNS, MAX_BATCH_ROWS, MODEL_NAME
from utils.helpers import (
    get_prediction_text,
    get_recommendation,
    get_risk_level,
    probability_to_percentage,
    transaction_assessment,
)


def validate_feature_vector(input_data):
    if len(input_data) != len(FEATURE_COLUMNS):
        raise ValueError(
            f"Expected {len(FEATURE_COLUMNS)} features but received {len(input_data)}."
        )

    try:
        input_array = np.asarray(input_data, dtype=float).reshape(1, -1)
    except (TypeError, ValueError) as exc:
        raise ValueError("All transaction features must be numeric.") from exc

    if not np.isfinite(input_array).all():
        raise ValueError("Transaction features cannot contain NaN or infinite values.")

    if input_array[0, FEATURE_COLUMNS.index("Amount")] < 0:
        raise ValueError("Amount cannot be negative.")

    if input_array[0, FEATURE_COLUMNS.index("Time")] < 0:
        raise ValueError("Time cannot be negative.")

    return input_array


def validate_feature_mapping(values: dict) -> dict:
    missing = [column for column in FEATURE_COLUMNS if column not in values]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    parsed = {}
    for column in FEATURE_COLUMNS:
        raw_value = values.get(column)
        if raw_value in (None, ""):
            raise ValueError(f"{column} is required.")
        try:
            parsed[column] = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{column} must be numeric.") from exc

    validate_feature_vector([parsed[column] for column in FEATURE_COLUMNS])
    return parsed


def prepare_feature_frame(input_data) -> pd.DataFrame:
    input_array = validate_feature_vector(input_data)
    return pd.DataFrame(input_array, columns=FEATURE_COLUMNS)


def prepare_batch_features(df, max_rows=MAX_BATCH_ROWS):
    if df.empty:
        raise ValueError("The uploaded CSV is empty.")

    if len(df) > max_rows:
        raise ValueError(
            f"Batch upload is limited to {max_rows:,} rows. Split the file and try again."
        )

    cleaned = df.copy()

    if "Class" in cleaned.columns:
        cleaned = cleaned.drop(columns=["Class"])

    missing_columns = [col for col in FEATURE_COLUMNS if col not in cleaned.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    cleaned = cleaned[FEATURE_COLUMNS]
    cleaned = cleaned.apply(pd.to_numeric, errors="coerce")

    if cleaned.isnull().values.any():
        raise ValueError("The uploaded CSV contains invalid or missing numeric values.")

    if not np.isfinite(cleaned.to_numpy(dtype=float)).all():
        raise ValueError("The uploaded CSV contains NaN or infinite values.")

    if (cleaned["Amount"] < 0).any():
        raise ValueError("Amount values cannot be negative.")

    if (cleaned["Time"] < 0).any():
        raise ValueError("Time values cannot be negative.")

    return cleaned


def _fraud_probabilities(model, scaled_features):
    if not hasattr(model, "predict_proba"):
        return None

    probabilities = model.predict_proba(scaled_features)
    classes = list(getattr(model, "classes_", []))
    if 1 in classes:
        fraud_index = classes.index(1)
    elif probabilities.shape[1] > 1:
        fraud_index = 1
    else:
        return None

    return probabilities[:, fraud_index].astype(float)


def predict_batch(model, scaler, df):
    features = prepare_batch_features(df)
    scaled = scaler.transform(features)
    predictions = np.asarray(model.predict(scaled), dtype=int)
    probabilities = _fraud_probabilities(model, scaled)

    results = features.copy()
    results["Prediction"] = [get_prediction_text(item) for item in predictions]
    if probabilities is None:
        results["Fraud Probability"] = None
        probability_values = np.array([np.nan] * len(results), dtype=float)
    else:
        probability_values = probabilities
        results["Fraud Probability"] = probabilities

    return results, predictions, probability_values


def predict_transaction(model, scaler, input_data):
    feature_frame = prepare_feature_frame(input_data)
    scaled_input = scaler.transform(feature_frame)
    prediction = int(model.predict(scaled_input)[0])
    probabilities = _fraud_probabilities(model, scaled_input)
    probability = None if probabilities is None else float(probabilities[0])
    return prediction, probability


def score_transaction(model, scaler, values: dict) -> dict:
    features = validate_feature_mapping(values)
    ordered_values = [features[column] for column in FEATURE_COLUMNS]
    prediction, probability = predict_transaction(model, scaler, ordered_values)
    probability_percent = probability_to_percentage(probability)
    risk_level = get_risk_level(probability)
    amount = float(features["Amount"])
    timestamp = datetime.now(timezone.utc)

    return {
        "transaction_id": str(uuid.uuid4())[:8],
        "timestamp": timestamp.isoformat(timespec="seconds"),
        "created_at": timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "prediction": prediction,
        "prediction_text": get_prediction_text(prediction),
        "probability": probability,
        "probability_percent": probability_percent,
        "probability_display": "Unavailable" if probability_percent is None else f"{probability_percent:.2f}%",
        "risk_level": risk_level,
        "recommendation": get_recommendation(probability),
        "amount": amount,
        "features": features,
        "feature_values": ordered_values,
        "model_name": MODEL_NAME,
        "assessment": transaction_assessment(prediction, probability, amount, risk_level),
    }


def enrich_batch_results(results: pd.DataFrame, predictions, probabilities) -> pd.DataFrame:
    enriched = results.copy()

    if "Prediction" not in enriched.columns:
        enriched["Prediction"] = [get_prediction_text(item) for item in predictions]

    if probabilities is None or np.isnan(probabilities).all():
        enriched["Fraud Probability"] = None
        enriched["Risk Level"] = "UNAVAILABLE"
        enriched["Recommended Action"] = get_recommendation(None)
        return enriched

    probability_values = np.asarray(probabilities, dtype=float)
    enriched["Fraud Probability"] = (probability_values * 100).round(2)
    enriched["Risk Level"] = [get_risk_level(probability) for probability in probability_values]
    enriched["Recommended Action"] = [get_recommendation(probability) for probability in probability_values]
    return enriched
