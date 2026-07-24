import numpy as np
import pandas as pd


def load_dashboard_data():
    try:
        return pd.read_csv("dataset/creditcard.csv"), False
    except FileNotFoundError:
        return generate_demo_transactions(), True


def generate_demo_transactions(rows=2400):
    rng = np.random.default_rng(42)

    data = {
        "Time": np.arange(rows) * 12,
        "Amount": rng.gamma(shape=2.0, scale=42.0, size=rows).round(2),
        "Class": np.zeros(rows, dtype=int),
    }

    fraud_indices = rng.choice(rows, size=max(12, rows // 120), replace=False)
    data["Class"][fraud_indices] = 1
    data["Amount"][fraud_indices] = rng.gamma(
        shape=3.2,
        scale=95.0,
        size=len(fraud_indices),
    ).round(2)

    for i in range(1, 29):
        values = rng.normal(0, 1, rows)
        values[fraud_indices] += rng.normal(1.2, 0.35, len(fraud_indices))
        data[f"V{i}"] = values.round(6)

    columns = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount", "Class"]
    return pd.DataFrame(data)[columns]
