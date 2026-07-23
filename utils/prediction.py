import numpy as np


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

    if len(input_data) != 30:
        raise ValueError(
            f"Expected 30 features but received {len(input_data)}."
        )

    # Convert to NumPy array
    input_array = np.asarray(input_data, dtype=float).reshape(1, -1)

    # Scale the input
    scaled_input = scaler.transform(input_array)

    # Predict
    prediction = int(model.predict(scaled_input)[0])

    # Probability of Fraud (Class = 1)
    probability = float(
        model.predict_proba(scaled_input)[0][1]
    )

    return prediction, probability