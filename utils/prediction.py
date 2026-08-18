import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "Time",
    "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9",
    "V10", "V11", "V12", "V13", "V14", "V15", "V16", "V17",
    "V18", "V19", "V20", "V21", "V22", "V23", "V24",
    "V25", "V26", "V27", "V28",
    "Amount",
]


MAX_BATCH_ROWS = 100_000


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

    if input_array[0, -1] < 0:
        raise ValueError("Amount cannot be negative.")

    if input_array[0, 0] < 0:
        raise ValueError("Time cannot be negative.")

    return input_array


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


def predict_batch(model, scaler, df):
    features = prepare_batch_features(df)
    scaled = scaler.transform(features)
    predictions = model.predict(scaled)
    probabilities = model.predict_proba(scaled)[:, 1]

    results = features.copy()
    results["Prediction"] = predictions
    results["Fraud Probability"] = probabilities

    return results, predictions, probabilities


def predict_transaction(model, scaler, input_data):
    """
    Predict whether a credit card transaction is fraudulent.

    Parameters
    ----------
    model : sklearn model
        Trained Random Forest model.

    scaler : sklearn scaler
        Trained StandardScaler.

    input_data : list
        List containing exactly 30 feature values.

    Returns
    -------
    prediction : int
        0 -> Genuine Transaction
        1 -> Fraudulent Transaction

    probability : float
        Fraud probability (0.0 - 1.0)
    """

    input_array = validate_feature_vector(input_data)

    input_df = pd.DataFrame(input_array, columns=FEATURE_COLUMNS)

    # Scale the input
    scaled_input = scaler.transform(input_df)

    # Predict
    prediction = int(model.predict(scaled_input)[0])

    # Probability of Fraud (Class = 1)
    probability = float(
        model.predict_proba(scaled_input)[0][1]
    )

    return prediction, probability
