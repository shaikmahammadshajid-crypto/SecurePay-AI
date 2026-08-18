import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PLOTLY_CONFIG = {"responsive": True, "displaylogo": False}


def _as_records(rows):
    return [dict(row) for row in rows] if rows else []


def _finish(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=24, r=18, t=34, b=28),
        font=dict(family="Inter, system-ui, sans-serif", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, config=PLOTLY_CONFIG)


def create_fraud_distribution_chart(rows):
    records = _as_records(rows)
    if not records:
        return None

    fraud = sum(1 for row in records if "Fraud" in str(row.get("prediction", "")))
    genuine = len(records) - fraud
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Fraud", "Genuine"],
                values=[fraud, genuine],
                hole=0.58,
                marker=dict(colors=["#ef6156", "#45c477"]),
            )
        ]
    )
    fig.update_layout(title="Fraud vs Genuine")
    return _finish(fig)


def create_risk_distribution_chart(risk_rows):
    records = _as_records(risk_rows)
    if not records:
        return None

    order = ["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNAVAILABLE"]
    df = pd.DataFrame(records)
    df["risk_level"] = pd.Categorical(df["risk_level"], categories=order, ordered=True)
    df = df.sort_values("risk_level")
    fig = px.bar(
        df,
        x="risk_level",
        y="total",
        color="risk_level",
        color_discrete_map={
            "LOW": "#45c477",
            "MEDIUM": "#d49a25",
            "HIGH": "#f08c2e",
            "CRITICAL": "#ef6156",
            "UNAVAILABLE": "#9fafb6",
        },
        title="Risk Distribution",
    )
    fig.update_layout(showlegend=False)
    return _finish(fig)


def create_prediction_trend_chart(rows):
    records = _as_records(rows)
    if not records:
        return None

    df = pd.DataFrame(records)
    if "created_at" not in df:
        return None

    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.dropna(subset=["created_at"])
    if df.empty:
        return None

    df["date"] = df["created_at"].dt.date
    df["fraud"] = df["prediction"].astype(str).str.contains("Fraud", case=False, na=False).astype(int)
    trend = df.groupby("date").agg(total=("id", "count"), fraud=("fraud", "sum")).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend["date"], y=trend["total"], mode="lines+markers", name="Total"))
    fig.add_trace(go.Scatter(x=trend["date"], y=trend["fraud"], mode="lines+markers", name="Fraud"))
    fig.update_layout(title="Prediction Trends", yaxis_title="Transactions")
    return _finish(fig)


def create_probability_chart(rows):
    records = _as_records(rows)
    if not records:
        return None

    df = pd.DataFrame(records)
    df["probability"] = pd.to_numeric(df.get("probability"), errors="coerce")
    df = df.dropna(subset=["probability"])
    if df.empty:
        return None

    fig = px.histogram(
        df,
        x="probability",
        nbins=20,
        title="Fraud Probability Distribution",
        labels={"probability": "Fraud probability (%)"},
        color_discrete_sequence=["#27a69a"],
    )
    return _finish(fig)


def create_amount_distribution_chart(rows):
    records = _as_records(rows)
    if not records:
        return None

    df = pd.DataFrame(records)
    df["amount"] = pd.to_numeric(df.get("amount"), errors="coerce")
    df = df.dropna(subset=["amount"])
    if df.empty:
        return None

    fig = px.histogram(
        df,
        x="amount",
        nbins=20,
        title="Transaction Amount Distribution",
        labels={"amount": "Amount"},
        color_discrete_sequence=["#7aa2ff"],
    )
    return _finish(fig)


def create_shap_chart(top_features):
    if not top_features:
        return None

    df = pd.DataFrame(top_features)
    fig = px.bar(
        df.sort_values("impact", ascending=True),
        x="shap_value",
        y="feature",
        orientation="h",
        color="direction",
        color_discrete_map={"increases fraud score": "#ef6156", "decreases fraud score": "#45c477"},
        title="Top SHAP Feature Attributions",
        labels={"shap_value": "SHAP value", "feature": "Feature"},
    )
    return _finish(fig)


def create_labeled_dataset_charts(df):
    if df is None or df.empty or "Class" not in df.columns:
        return {}

    charts = {}
    working = df.copy()
    working["Class"] = pd.to_numeric(working["Class"], errors="coerce")
    working = working.dropna(subset=["Class"])
    if working.empty:
        return charts

    counts = working["Class"].map({0: "Genuine", 1: "Fraud"}).value_counts().reset_index()
    counts.columns = ["label", "total"]
    charts["fraud_distribution"] = _finish(
        px.pie(
            counts,
            names="label",
            values="total",
            hole=0.58,
            title="Labeled Fraud Distribution",
            color="label",
            color_discrete_map={"Fraud": "#ef6156", "Genuine": "#45c477"},
        )
    )

    if "Amount" in working.columns:
        working["Amount"] = pd.to_numeric(working["Amount"], errors="coerce")
        amount_df = working.dropna(subset=["Amount"])
        if not amount_df.empty:
            amount_df["Class Label"] = amount_df["Class"].map({0: "Genuine", 1: "Fraud"})
            charts["amount_distribution"] = _finish(
                px.histogram(
                    amount_df,
                    x="Amount",
                    color="Class Label",
                    nbins=24,
                    title="Amount Distribution by Class",
                    color_discrete_map={"Fraud": "#ef6156", "Genuine": "#45c477"},
                )
            )

    return charts
