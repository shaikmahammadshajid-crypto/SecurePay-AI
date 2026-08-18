# SecurePay AI

SecurePay AI is a Render-hosted Flask web application for credit card fraud detection. It combines a trained Random Forest model, SQLite audit storage, bcrypt authentication, CSV batch screening, audit PDF reports, and an app-aware AI assistant command center.

## Features

- Secure login and registration with bcrypt password hashing
- Single transaction fraud prediction
- Batch CSV fraud screening
- Personalized AI Assistant command center
- Model and app health checks through `/health`
- User prediction history and profile summaries
- Admin dashboard for users, prediction logs, fraud counts, and batch jobs
- PDF audit report generation
- Reproducible model training script
- Automated pytest reliability suite

## Main Task

The main task of SecurePay AI is to detect potentially fraudulent credit card transactions. The app accepts transaction features, predicts whether the transaction is genuine or fraud, calculates fraud probability, assigns a risk level, recommends an action, and stores the result for audit.

## Reviewer Preparation

- Open the live app and select **Reviewer Guide**.
- Open **Public Demo** first if the reviewer wants to see the core task without login.
- Register or login.
- Open **Predict** and use a demo transaction.
- Review the prediction, fraud probability, risk level, and recommendation.
- Open **History** to show saved audit records.
- Open **AI Assistant** and run `check app health`, `summarize my activity`, or `generate my audit report`.
- Download the presentation PDF from **Presentation File**.
- Use `docs/SecurePayAI_Presentation.md` as preparation notes.

## Technology Stack

- Runtime: Flask + Gunicorn on Render
- Backend: Python
- Machine learning: scikit-learn, Joblib
- Data processing: Pandas, NumPy
- Database: SQLite
- Reports: ReportLab
- Tests: Pytest

## Project Structure

```text
SecurePayAI/
├── app.py
├── render.yaml
├── requirements.txt
├── .python-version
├── database/
├── models/
│   ├── random_forest.pkl
│   └── scaler.pkl
├── reports/
├── scripts/
│   └── train_model.py
├── static/
│   └── style.css
├── templates/
├── tests/
└── utils/
```

## Local Setup

```bash
git clone https://github.com/shaikmahammadshajid-crypto/SecurePay-AI.git
cd SecurePay-AI
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Production on Render

This repository is configured for Render with `render.yaml`.

- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
- Health check path: `/health`
- Python version: `.python-version` pins `3.11.9`
- Optional environment variable: `SECUREPAY_ADMIN_PASSWORD`

Live service:

https://securepay-ai-orhb.onrender.com

## Tests

```bash
python -m pytest -q
```

## Retrain Model

Place the credit card fraud dataset at `dataset/creditcard.csv`, then run:

```bash
python scripts/train_model.py
```

The training script writes updated model artifacts to `models/` and an evaluation report to `reports/model_evaluation.txt`.

## Accuracy Note

Fraud detection models should be evaluated with measured precision, recall, F1, ROC-AUC, and confusion matrix results. This project does not claim impossible 100% accuracy; it provides tests and training tooling so model quality can be measured against a labeled dataset.
