import os
import secrets
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

APP_NAME = "SecurePay AI"
APP_VERSION = "1"
APP_TITLE = "SecurePay AI - AI-Powered Credit Card Fraud Detection System"
ENVIRONMENT = os.getenv("SECUREPAY_ENV", os.getenv("FLASK_ENV", "development")).lower()

SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "").lower() in {"1", "true", "yes"}
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "8"))
MAX_BATCH_ROWS = int(os.getenv("MAX_BATCH_ROWS", "100000"))

DATABASE_PATH = Path(os.getenv("SECUREPAY_DB_PATH", BASE_DIR / "database" / "securepay.db"))
MODEL_PATH = Path(os.getenv("SECUREPAY_MODEL_PATH", BASE_DIR / "models" / "random_forest.pkl"))
SCALER_PATH = Path(os.getenv("SECUREPAY_SCALER_PATH", BASE_DIR / "models" / "scaler.pkl"))
DATASET_PATH = Path(os.getenv("SECUREPAY_DATASET_PATH", BASE_DIR / "dataset" / "creditcard.csv"))
REPORTS_DIR = Path(os.getenv("SECUREPAY_REPORTS_DIR", BASE_DIR / "reports" / "generated"))
MODEL_EVALUATION_PATH = Path(
    os.getenv("SECUREPAY_MODEL_EVALUATION_PATH", BASE_DIR / "reports" / "model_evaluation.txt")
)

FEATURE_COLUMNS = [
    "Time",
    "V1",
    "V2",
    "V3",
    "V4",
    "V5",
    "V6",
    "V7",
    "V8",
    "V9",
    "V10",
    "V11",
    "V12",
    "V13",
    "V14",
    "V15",
    "V16",
    "V17",
    "V18",
    "V19",
    "V20",
    "V21",
    "V22",
    "V23",
    "V24",
    "V25",
    "V26",
    "V27",
    "V28",
    "Amount",
]

# Fraud probability thresholds. Values are model probabilities from 0.0 to 1.0.
# LOW:      0.00 <= p < 0.30
# MEDIUM:   0.30 <= p < 0.60
# HIGH:     0.60 <= p < 0.85
# CRITICAL: 0.85 <= p <= 1.00
RISK_THRESHOLDS = {
    "MEDIUM": 0.30,
    "HIGH": 0.60,
    "CRITICAL": 0.85,
}

RISK_ACTIONS = {
    "LOW": "Approve under normal fraud-monitoring controls.",
    "MEDIUM": "Monitor the transaction and review contextual behavior.",
    "HIGH": "Request additional verification before approval.",
    "CRITICAL": "Block or hold the transaction and escalate to fraud review.",
    "UNAVAILABLE": "Review manually because the model did not provide a probability.",
}

MODEL_NAME = "Random Forest"
SCALER_NAME = "StandardScaler"
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@securepay.ai"
