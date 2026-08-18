import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from utils.prediction import FEATURE_COLUMNS


def train_model(dataset_path, model_path, scaler_path, report_path):
    df = pd.read_csv(dataset_path)

    missing_columns = [column for column in FEATURE_COLUMNS + ["Class"] if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing_columns)}")

    features = df[FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce")
    labels = df["Class"].astype(int)

    if features.isnull().values.any():
        raise ValueError("Dataset contains invalid or missing feature values.")

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced_subsample",
        n_jobs=-1,
    )
    model.fit(x_train_scaled, y_train)

    predictions = model.predict(x_test_scaled)
    probabilities = model.predict_proba(x_test_scaled)[:, 1]

    report = classification_report(y_test, predictions, digits=4)
    roc_auc = roc_auc_score(y_test, probabilities)
    matrix = confusion_matrix(y_test, predictions)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    report_path.write_text(
        "SecurePay AI Model Evaluation\n\n"
        f"ROC-AUC: {roc_auc:.6f}\n\n"
        f"Confusion Matrix:\n{matrix}\n\n"
        f"Classification Report:\n{report}\n",
        encoding="utf-8",
    )

    return roc_auc


def main():
    parser = argparse.ArgumentParser(description="Train and evaluate SecurePay AI fraud model.")
    parser.add_argument("--dataset", default="dataset/creditcard.csv", help="CSV with Time, V1-V28, Amount, Class.")
    parser.add_argument("--model", default="models/random_forest.pkl")
    parser.add_argument("--scaler", default="models/scaler.pkl")
    parser.add_argument("--report", default="reports/model_evaluation.txt")
    args = parser.parse_args()

    roc_auc = train_model(
        dataset_path=Path(args.dataset),
        model_path=Path(args.model),
        scaler_path=Path(args.scaler),
        report_path=Path(args.report),
    )

    print(f"Training complete. ROC-AUC: {roc_auc:.6f}")


if __name__ == "__main__":
    main()
