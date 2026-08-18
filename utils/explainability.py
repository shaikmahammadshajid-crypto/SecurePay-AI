import logging

import numpy as np
import pandas as pd

from config import FEATURE_COLUMNS


logger = logging.getLogger(__name__)


def _select_class_one_values(shap_values):
    values = shap_values
    if isinstance(values, list):
        values = values[1] if len(values) > 1 else values[0]

    values = np.asarray(values)
    if values.ndim == 3:
        values = values[:, :, 1] if values.shape[2] > 1 else values[:, :, 0]
    if values.ndim == 2:
        return values[0]
    if values.ndim == 1:
        return values
    raise ValueError("Unexpected SHAP value shape.")


def explain_transaction(model, scaler, features: dict, limit=8) -> dict:
    try:
        import shap
    except Exception:
        return {
            "available": False,
            "message": "SHAP is not installed in this environment.",
            "technical": "Install the shap dependency to enable model feature attribution.",
            "simple": "Feature explanation is unavailable for this run.",
            "top_features": [],
        }

    try:
        ordered = [float(features[column]) for column in FEATURE_COLUMNS]
        feature_frame = pd.DataFrame([ordered], columns=FEATURE_COLUMNS)
        scaled = scaler.transform(feature_frame)
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(scaled)
        class_values = _select_class_one_values(shap_values)

        top_indexes = np.argsort(np.abs(class_values))[::-1][:limit]
        top_features = []
        for index in top_indexes:
            shap_value = float(class_values[index])
            top_features.append(
                {
                    "feature": FEATURE_COLUMNS[index],
                    "input_value": ordered[index],
                    "shap_value": round(shap_value, 6),
                    "impact": round(abs(shap_value), 6),
                    "direction": "increases fraud score" if shap_value >= 0 else "decreases fraud score",
                }
            )

        strongest = top_features[0] if top_features else None
        if strongest:
            simple = (
                f"The strongest model attribution is {strongest['feature']}, which "
                f"{strongest['direction']} for this prediction."
            )
        else:
            simple = "No dominant feature attribution was returned for this transaction."

        return {
            "available": True,
            "message": "SHAP feature attribution is available.",
            "technical": (
                "SHAP values estimate how each scaled model feature contributed to this "
                "Random Forest prediction. They are model attributions, not proof of causality."
            ),
            "simple": simple,
            "top_features": top_features,
        }
    except Exception as exc:
        logger.exception("SHAP explanation failed")
        return {
            "available": False,
            "message": "SHAP explanation could not be generated for this transaction.",
            "technical": str(exc),
            "simple": "The prediction is still valid, but feature attribution is unavailable.",
            "top_features": [],
        }
