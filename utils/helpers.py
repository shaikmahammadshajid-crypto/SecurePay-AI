"""
Helper functions used throughout SecurePay AI.
"""


def get_risk_level(probability: float) -> str:
    """
    Convert fraud probability into a human-readable risk level.

    Parameters
    ----------
    probability : float
        Fraud probability between 0 and 1.

    Returns
    -------
    str
        Risk level with colored indicator.
    """

    if probability < 0.30:
        return "🟢 LOW"

    elif probability < 0.60:
        return "🟡 MEDIUM"

    elif probability < 0.85:
        return "🟠 HIGH"

    return "🔴 CRITICAL"


def get_prediction_text(prediction: int) -> str:
    """
    Convert model prediction into readable text.
    """

    if prediction == 1:
        return "🚨 Fraud Transaction"

    return "✅ Genuine Transaction"


def get_recommendation(probability: float) -> str:
    """
    Generate an AI recommendation based on fraud probability.
    """

    if probability < 0.30:
        return "✅ Approve the transaction."

    elif probability < 0.60:
        return "🟡 Monitor the transaction."

    elif probability < 0.85:
        return "🟠 Request additional verification."

    return "🔴 Block the transaction immediately."


def probability_to_percentage(probability: float) -> float:
    """
    Convert probability into percentage.
    """

    return round(probability * 100, 2)