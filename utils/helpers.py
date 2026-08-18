"""
Shared presentation and risk helpers for SecurePay AI.
"""

from config import RISK_ACTIONS, RISK_THRESHOLDS


def get_risk_level(probability: float | None) -> str:
    """Classify a fraud probability into the configured risk bands."""
    if probability is None:
        return "UNAVAILABLE"

    probability = float(probability)
    if probability < RISK_THRESHOLDS["MEDIUM"]:
        return "LOW"
    if probability < RISK_THRESHOLDS["HIGH"]:
        return "MEDIUM"
    if probability < RISK_THRESHOLDS["CRITICAL"]:
        return "HIGH"
    return "CRITICAL"


def get_prediction_text(prediction: int) -> str:
    if int(prediction) == 1:
        return "Fraud Transaction"
    return "Genuine Transaction"


def get_recommendation(probability: float | None) -> str:
    risk_level = get_risk_level(probability)
    return RISK_ACTIONS.get(risk_level, RISK_ACTIONS["UNAVAILABLE"])


def probability_to_percentage(probability: float | None) -> float | None:
    if probability is None:
        return None
    return round(float(probability) * 100, 2)


def format_probability(probability_percent: float | None) -> str:
    if probability_percent is None:
        return "Unavailable"
    return f"{float(probability_percent):.2f}%"


def risk_level_class(risk_level: str) -> str:
    normalized = (risk_level or "").lower()
    if "critical" in normalized:
        return "critical"
    if "high" in normalized:
        return "high"
    if "medium" in normalized:
        return "medium"
    if "low" in normalized:
        return "low"
    return "unknown"


def transaction_assessment(prediction: int, probability: float | None, amount: float, risk_level: str) -> dict:
    if probability is None:
        return {
            "decision": "Manual review required",
            "action": RISK_ACTIONS["UNAVAILABLE"],
            "review": "The classifier returned a class label without a calibrated fraud probability.",
            "summary": f"Amount ${amount:,.2f} was classified as {risk_level}.",
        }

    recommendation = get_recommendation(probability)
    if risk_level == "CRITICAL":
        review = "Escalate for immediate fraud review and verify the transaction through trusted channels."
    elif risk_level == "HIGH":
        review = "Review customer behavior, transaction velocity, and recent account activity before approval."
    elif risk_level == "MEDIUM":
        review = "Compare this transaction against normal amount and timing patterns."
    else:
        review = "Keep the prediction in the audit trail and continue normal monitoring."

    return {
        "decision": "Fraud review required" if int(prediction) == 1 else "Likely genuine",
        "action": recommendation,
        "review": review,
        "summary": (
            f"Amount ${amount:,.2f} is classified as {risk_level} with "
            f"{probability * 100:.2f}% fraud probability."
        ),
    }


def batch_assessment(total: int, fraud: int, genuine: int, fraud_rate: float) -> dict:
    if fraud_rate >= 10:
        action = "Critical batch anomaly. Review the highest-risk rows before downstream use."
    elif fraud_rate >= 2:
        action = "Elevated fraud concentration. Prioritize high-probability rows for review."
    elif fraud > 0:
        action = "Fraud detected. Export the report and inspect flagged transactions first."
    else:
        action = "No fraud was flagged. Keep the report as an audit record."

    return {
        "summary": f"Screened {total:,} transactions: {fraud:,} fraud and {genuine:,} genuine.",
        "action": action,
        "fraud_rate": fraud_rate,
    }
