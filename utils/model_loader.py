import logging
from functools import lru_cache
from pathlib import Path

import joblib

from config import FEATURE_COLUMNS, MODEL_EVALUATION_PATH, MODEL_NAME, MODEL_PATH, SCALER_NAME, SCALER_PATH


logger = logging.getLogger(__name__)


def _load_joblib(path: Path, label: str):
    if not path.exists():
        raise FileNotFoundError(f"{label} file is missing. Expected: {path}")
    if path.stat().st_size == 0:
        raise RuntimeError(f"{label} file is empty. Expected a valid joblib artifact at {path}")

    try:
        return joblib.load(path)
    except Exception as exc:
        logger.exception("Failed to load %s artifact from %s", label, path)
        raise RuntimeError(f"{label} file could not be loaded. Verify the artifact is valid.") from exc


def _validate_feature_count(obj, label: str):
    expected = len(FEATURE_COLUMNS)
    actual = getattr(obj, "n_features_in_", expected)
    if int(actual) != expected:
        raise RuntimeError(f"{label} expects {actual} features, but SecurePay AI requires {expected}.")


def _validate_feature_names(obj, label: str):
    names = getattr(obj, "feature_names_in_", None)
    if names is None:
        return

    artifact_features = list(names)
    if artifact_features != FEATURE_COLUMNS:
        raise RuntimeError(f"{label} feature order does not match SecurePay AI Version 1 schema.")


def validate_model(model):
    if not hasattr(model, "predict"):
        raise RuntimeError("Model artifact does not expose predict().")
    _validate_feature_count(model, "Model")
    _validate_feature_names(model, "Model")
    return True


def validate_scaler(scaler):
    if not hasattr(scaler, "transform"):
        raise RuntimeError("Scaler artifact does not expose transform().")
    _validate_feature_count(scaler, "Scaler")
    _validate_feature_names(scaler, "Scaler")
    return True


@lru_cache(maxsize=1)
def load_model():
    model = _load_joblib(MODEL_PATH, "Model")
    validate_model(model)
    return model


@lru_cache(maxsize=1)
def load_scaler():
    scaler = _load_joblib(SCALER_PATH, "Scaler")
    validate_scaler(scaler)
    return scaler


def get_model_info() -> dict:
    info = {
        "model_name": MODEL_NAME,
        "scaler_name": SCALER_NAME,
        "feature_count": len(FEATURE_COLUMNS),
        "model_path": MODEL_PATH.as_posix(),
        "scaler_path": SCALER_PATH.as_posix(),
        "probability_supported": False,
        "status": "Unavailable",
        "metrics_available": MODEL_EVALUATION_PATH.exists(),
        "metrics": "Model metrics have not been calculated in this repository.",
    }

    try:
        model = load_model()
        load_scaler()
        info.update(
            {
                "status": "Ready",
                "model_type": type(model).__name__,
                "probability_supported": hasattr(model, "predict_proba"),
                "estimators": getattr(model, "n_estimators", None),
            }
        )
    except Exception as exc:
        info["status"] = "Attention"
        info["error"] = str(exc)
        return info

    if MODEL_EVALUATION_PATH.exists():
        try:
            info["metrics"] = MODEL_EVALUATION_PATH.read_text(encoding="utf-8")
        except OSError:
            logger.exception("Could not read model evaluation file")
            info["metrics"] = "Model metrics file exists but could not be read."

    return info
