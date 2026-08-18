# 🧠 SecurePay AI

## 🚀 AI-Powered Credit Card Fraud Detection System, Risk Analytics Console & Audit Report Engine

An intelligent, production-ready web application designed to help users detect suspicious credit-card transactions, run manual fraud prediction, upload CSV batches, analyze fraud trends, review prediction history, generate PDF reports, and monitor model/system health using a trained Random Forest machine-learning pipeline.

Python Flask SQLite Random Forest SHAP Plotly PDF Reports Status

## 📌 Project Overview

SecurePay AI is a professional Version 1 credit-card fraud detection platform built around a trained Random Forest classifier and StandardScaler preprocessing pipeline. It combines user authentication, manual transaction scoring, batch CSV fraud prediction, SHAP-ready explainability, Plotly analytics, prediction history, PDF audit reports, admin monitoring, and secure SQLite persistence into one focused web application.

The system preserves the original SecurePay AI Version 1 goal: AI-powered credit-card fraud detection. It does not add UPI, wallet, banking, crypto, payment-gateway, or native mobile-app features. The application is designed for college project submission, viva demonstration, hackathon review, GitHub portfolio use, and internship portfolio presentation.

## ✨ Key Features

🏠 **Professional Dashboard:** Shows total transactions, fraud detected, genuine transactions, fraud rate, average fraud probability, recent predictions, readiness checks, and quick actions.

🔐 **Secure Authentication:** Supports registration, login, logout, bcrypt password hashing, duplicate username/email handling, secure sessions, and generic invalid-credential responses.

🧾 **Manual Fraud Prediction:** Lets users enter all 30 required model features, runs the trained Random Forest pipeline, saves the result, and shows classification, fraud probability, risk level, amount, timestamp, and model information.

📂 **Batch CSV Prediction:** Uploads transaction CSV files, validates required columns and numeric values, scores every row, summarizes fraud statistics, and generates downloadable CSV, Excel, and PDF outputs.

📊 **Fraud Analytics Dashboard:** Includes fraud vs genuine distribution, risk distribution, prediction trends, fraud probability distribution, transaction amount distribution, and labeled dataset analytics.

📜 **Prediction History:** Displays saved predictions with ID, username, transaction ID, prediction, probability, amount, risk level, created time, filtering, sorting, searching, and PDF links.

📄 **PDF Report Engine:** Generates professional SecurePay AI reports for single predictions, audit history, and batch summaries using ReportLab.

🧠 **SHAP Explainability:** Provides model feature attribution where compatible, including technical explanation, simple explanation, top contributing features, and attribution charts.

🛡️ **Centralized Risk Classification:** Uses configurable LOW, MEDIUM, HIGH, and CRITICAL risk thresholds from one configuration file.

🧪 **Model Health & Metrics:** Validates model/scaler availability, feature count, feature order, probability support, and displays real metrics only when calculated.

🛠️ **Admin Dashboard:** Enables authorized admins to view users, predictions, fraud totals, batch jobs, risk distribution, model status, readiness checks, and manage user roles.

📱 **Responsive Dark UI:** Provides a polished fintech/cybersecurity interface with dark theme, responsive cards, mobile-friendly tables, touch-friendly forms, and professional empty/error states.

## 🤖 Fraud Detection Engine

| Component | Purpose |
| --- | --- |
| Input Validation | Checks required fields, numeric values, missing values, finite values, non-negative Time, and non-negative Amount |
| Feature Schema | Preserves the exact trained 30-feature order from `config.py` |
| StandardScaler | Applies the saved scaler before inference |
| Random Forest Model | Predicts genuine or fraudulent credit-card transaction class |
| Probability Handler | Uses `predict_proba` only when supported and never fabricates probability values |
| Risk Classifier | Converts fraud probability into LOW, MEDIUM, HIGH, or CRITICAL |
| SHAP Explainer | Generates model feature attribution when compatible |
| SQLite Audit Store | Saves predictions and batch summaries for history, analytics, and reports |
| PDF Report Service | Creates single, batch, and audit reports with SecurePay AI branding |
| Admin Monitor | Tracks users, model status, fraud activity, and prediction logs |

## 🛠️ Technology Stack

### Backend & Web Runtime

- **Language:** Python
- **Framework:** Flask
- **Production Server:** Gunicorn
- **Deployment:** Render Blueprint using `render.yaml`
- **Health Check:** `/health`

### Machine Learning

- **Model:** Random Forest classifier
- **Preprocessing:** StandardScaler
- **Model Loading:** joblib with cached reusable loaders
- **ML Libraries:** scikit-learn, NumPy, pandas
- **Explainability:** SHAP where compatible

### Data, Reports & Analytics

- **Database:** SQLite
- **Charts:** Plotly
- **PDF Reports:** ReportLab
- **Excel Export:** openpyxl
- **CSV Processing:** pandas

### Security & Quality

- **Password Hashing:** bcrypt
- **Authorization:** Server-side role checks
- **Validation:** Manual input and CSV upload validation
- **Testing:** pytest
- **Configuration:** Centralized `config.py`
- **Secrets:** Environment variables, no hardcoded production secrets

## 📂 Project Structure

```text
SecurePayAI/
│
├── app.py                          # Flask routes, auth guards, prediction pages, reports, health
├── config.py                       # Central app config, feature schema, paths, risk thresholds
├── requirements.txt                # Python dependencies
├── render.yaml                     # Render deployment configuration
├── runtime.txt                     # Runtime hint
├── README.md                       # Project documentation
│
├── database/
│   ├── __init__.py
│   ├── admin.py                    # Admin stats, batch summaries, role management
│   ├── auth.py                     # Registration, login, bcrypt hashing, authentication
│   ├── db.py                       # SQLite connection, schema creation, admin seeding
│   ├── history.py                  # Prediction persistence, history reads, feature metadata
│   └── profile.py                  # User profile queries
│
├── models/
│   ├── random_forest.pkl           # Trained Random Forest fraud model
│   └── scaler.pkl                  # Saved StandardScaler artifact
│
├── reports/
│   ├── pdf_generator.py            # Single, batch, and audit PDF report generation
│   └── generated/                  # Generated report downloads
│
├── scripts/
│   └── train_model.py              # Optional retraining script and metrics generation
│
├── static/
│   ├── app.js                      # UI interactions, tables, theme, chart resize helpers
│   └── style.css                   # Responsive dark fintech/cybersecurity UI
│
├── templates/
│   ├── base.html                   # App shell, sidebar, alerts, global layout
│   ├── login.html                  # Login and registration
│   ├── dashboard.html              # User dashboard
│   ├── predict.html                # Manual prediction and SHAP result view
│   ├── batch.html                  # CSV batch prediction and downloads
│   ├── analytics.html              # Analytics charts and model metrics
│   ├── history.html                # Prediction history with filtering
│   ├── reports.html                # Reports workspace
│   ├── profile.html                # User profile and recent predictions
│   ├── about.html                  # Project/model overview
│   ├── admin.html                  # Admin dashboard and role management
│   ├── error.html                  # Friendly error page
│   └── partials/
│       ├── simple_table.html       # Reusable responsive table
│       └── table.html              # Batch result table
│
├── tests/
│   ├── test_app_health.py
│   ├── test_auth.py
│   ├── test_flask_app.py
│   ├── test_helpers.py
│   ├── test_model_artifacts.py
│   ├── test_prediction.py
│   └── test_runtime_config.py
│
└── utils/
    ├── app_health.py               # Runtime readiness checks
    ├── charts.py                   # Plotly chart service
    ├── explainability.py           # SHAP attribution service
    ├── helpers.py                  # Risk, probability, recommendation helpers
    ├── model_loader.py             # Cached model/scaler loading and validation
    └── prediction.py               # Feature validation and prediction service
```

## 🚀 Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/shaikmahammadshajid-crypto/SecurePay-AI.git
```

### 2. Navigate to Directory

```bash
cd SecurePay-AI
```

### 3. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Set Environment Variables

```bash
export SECRET_KEY="change-this-in-production"
export SECUREPAY_ADMIN_PASSWORD="your_admin_password"
export SESSION_COOKIE_SECURE="false"
export MAX_UPLOAD_MB="8"
```

### 6. Run Development Server

```bash
python app.py
```

The application will launch on:

```text
http://127.0.0.1:5000
```

If port `5000` is occupied:

```bash
PORT=5001 python app.py
```

### 7. Run Production Server Locally

```bash
gunicorn app:app --bind 0.0.0.0:5000
```

### 8. Run Tests

```bash
python -m pytest -q
```

## 🧬 Required Model Features

The trained model uses exactly these 30 features. The order is centralized in `config.py` and reused across manual prediction, batch prediction, reports, SHAP, tests, and training.

```text
Time,
V1,
V2,
V3,
V4,
V5,
V6,
V7,
V8,
V9,
V10,
V11,
V12,
V13,
V14,
V15,
V16,
V17,
V18,
V19,
V20,
V21,
V22,
V23,
V24,
V25,
V26,
V27,
V28,
Amount
```

## 📊 Fraud Detection Workflow

```text
User Input or CSV Upload
          │
          ▼
Input Validation
          │
          ▼
Extract Exact 30 Features
          │
          ▼
Apply Correct Feature Order
          │
          ▼
StandardScaler Transform
          │
          ▼
Random Forest Prediction
          │
          ▼
Fraud Probability if Supported
          │
          ▼
Risk Classification
          │
          ├───────────────┬─────────────────┬──────────────────┐
          ▼               ▼                 ▼                  ▼
        LOW             MEDIUM             HIGH             CRITICAL
          │               │                 │                  │
          ▼               ▼                 ▼                  ▼
     Normal Review   Monitor Context   Verify Carefully   Block or Hold
          │               │                 │                  │
          └───────────────┴─────────────────┴──────────────────┘
                                  │
                                  ▼
                        Optional SHAP Attribution
                                  │
                                  ▼
                         Save SQLite Audit Record
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
          Dashboard / History              PDF / CSV / Excel Reports
```

## ⚠️ Risk Classification

Risk thresholds are configurable in `config.py`.

| Risk Level | Fraud Probability |
| --- | --- |
| LOW | `< 30%` |
| MEDIUM | `30% - 59.99%` |
| HIGH | `60% - 84.99%` |
| CRITICAL | `>= 85%` |

The app never invents probability values. If a future model does not support `predict_proba`, probability is shown as unavailable.

## 📄 CSV Format

Batch prediction CSV files must contain:

```text
Time,V1,V2,V3,V4,V5,V6,V7,V8,V9,V10,V11,V12,V13,V14,V15,V16,V17,V18,V19,V20,V21,V22,V23,V24,V25,V26,V27,V28,Amount
```

The app validates:

- `.csv` file extension
- required columns
- missing columns
- empty files
- invalid numeric values
- missing values
- NaN or infinite values
- negative `Time`
- negative `Amount`
- maximum upload size
- maximum row count

Download a sample template from:

```text
/sample-batch.csv
```

## 🔒 Security & Privacy Features

- **bcrypt Password Hashing:** Passwords are never stored as plaintext.
- **Generic Login Errors:** The app does not reveal whether username or password is wrong.
- **Server-Side Authorization:** Admin pages are protected by backend role checks.
- **Parameterized SQL:** SQLite queries avoid string concatenation with user input.
- **Secure Sessions:** HTTP-only cookies, same-site cookies, and optional secure cookies.
- **Safe Upload Handling:** CSV files are validated before model execution.
- **No Hardcoded Production Secrets:** Secret key and admin password are loaded from environment variables.
- **No Sensitive Debug Logs:** Passwords, hashes, and secrets are not logged.
- **Git Ignore Protection:** `.env`, local databases, generated reports, keys, and service-account JSON files are ignored.

## 📷 Key Application Views

🏠 **Dashboard:** Fraud totals, genuine totals, average fraud probability, recent predictions, health checks, and quick actions.

🧾 **Manual Prediction:** Full 30-feature form, sample transactions, actual Random Forest prediction, risk level, recommendation, and SHAP attribution.

📂 **Batch CSV Prediction:** CSV upload, validation, model scoring, fraud statistics, preview table, CSV download, Excel download, and PDF report download.

📊 **Analytics:** Fraud distribution, risk distribution, prediction trends, probability distribution, amount distribution, model metrics, and labeled CSV analysis.

📜 **Prediction History:** Searchable, sortable, filterable prediction audit log with per-transaction PDF reports.

📄 **Reports:** Audit PDF generation, recent single-prediction reports, model information, and recent batch summaries.

👤 **Profile:** User account details, prediction statistics, average fraud probability, and recent predictions.

🛠️ **Admin Dashboard:** Users, role management, predictions, batch jobs, risk distribution, model status, and readiness checks.

ℹ️ **About:** Dataset, model, scaler, SHAP, analytics, technology stack, feature schema, and responsible-use explanation.

## 🧪 Testing & Quality

Run the full test suite:

```bash
python -m pytest -q
```

Run syntax checks:

```bash
python -m compileall app.py config.py database utils reports scripts tests
```

Run model smoke test:

```bash
python - <<'PY'
from config import FEATURE_COLUMNS
from utils.model_loader import load_model, load_scaler, get_model_info
from utils.prediction import predict_transaction

model = load_model()
scaler = load_scaler()
print(get_model_info())
print(predict_transaction(model, scaler, [0.0] * 29 + [100.0]))
PY
```

## 🧠 Model Metrics

SecurePay AI displays only metrics that exist or can be calculated. If `reports/model_evaluation.txt` is missing, the UI clearly states that model metrics have not been calculated.

Optional metrics can include:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Confusion Matrix

To retrain and generate metrics, place the dataset at:

```text
dataset/creditcard.csv
```

Then run:

```bash
python scripts/train_model.py
```

The training script writes:

```text
models/random_forest.pkl
models/scaler.pkl
reports/model_evaluation.txt
```

Do not replace the trained model unless you preserve the expected 30-feature schema.

## 🌐 Live Demo & Repository

💻 **GitHub Repository:** https://github.com/shaikmahammadshajid-crypto/SecurePay-AI

🧪 **Local Development URL:** http://127.0.0.1:5000

🩺 **Health Endpoint:** `/health`

🚀 **Render Deployment:** This repository includes `render.yaml` for Blueprint deployment. Set `SECRET_KEY`, `SECUREPAY_ADMIN_PASSWORD`, `SESSION_COOKIE_SECURE`, and `MAX_UPLOAD_MB` in Render environment variables.

## 🚀 Deployment

### Render Build Command

```bash
pip install -r requirements.txt
```

### Render Start Command

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

### Required Render Environment Variables

```text
SECRET_KEY=strong_random_secret
SECUREPAY_ADMIN_PASSWORD=strong_admin_password
SESSION_COOKIE_SECURE=true
MAX_UPLOAD_MB=8
```

## 🚀 Future Enhancements

- PostgreSQL support for production persistence
- Admin export filters for large audit logs
- Model drift and calibration monitoring
- Saved SHAP report snapshots
- Advanced batch report pagination
- CI/CD workflow for automated tests
- Docker deployment profile
- Optional cloud storage for generated reports
- Role-specific audit events
- More model evaluation dashboards

## 👨‍💻 Author

**Shaik Mahammad Shajid**

B.Tech Computer Science & Engineering (Data Science)

Presidency University

GitHub: [@shaikmahammadshajid-crypto](https://github.com/shaikmahammadshajid-crypto)

## 📜 License

This project is developed for educational, credit-card fraud detection, AI/ML learning, and academic portfolio purposes.

⭐ If you found this project helpful, please consider giving it a Star on GitHub! ⭐
