import os
import uuid
from functools import wraps
from io import StringIO
from urllib.parse import quote

import pandas as pd
from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from database.admin import get_all_predictions, get_all_users, get_dashboard_stats
from database.auth import authenticate, normalize_username, register_account
from database.db import get_connection
from database.history import get_user_history, save_prediction
from database.profile import get_user_profile
from utils.ai_assistant import (
    detect_app_intent,
    get_assistant_answer,
    get_batch_assessment,
    get_transaction_assessment,
    summarize_user_history,
)
from utils.app_health import get_app_health, health_summary
from utils.helpers import (
    get_prediction_text,
    get_recommendation,
    get_risk_level,
    probability_to_percentage,
)
from utils.model_loader import load_model, load_scaler
from utils.prediction import FEATURE_COLUMNS, predict_batch, predict_transaction


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "securepay-dev-secret-change-me")


ROUTES = {
    "dashboard": "dashboard",
    "predict": "predict",
    "batch": "batch",
    "analytics": "analytics",
    "history": "history",
    "profile": "profile",
    "admin": "admin",
    "assistant": "assistant",
    "about": "about",
    "reviewer": "reviewer_guide",
}


DEMO_TRANSACTIONS = {
    "baseline": {
        "label": "Baseline Review Transaction",
        "description": "A simple low-complexity transaction profile for demonstrating the full prediction workflow.",
        "values": {
            **{column: "0" for column in FEATURE_COLUMNS},
            "Amount": "100",
        },
    },
    "high_amount": {
        "label": "High Amount Review Transaction",
        "description": "A larger payment profile that helps reviewers see probability, risk level, and recommendation behavior.",
        "values": {
            **{column: "0" for column in FEATURE_COLUMNS},
            "Time": "86400",
            "V1": "-1.35",
            "V2": "1.12",
            "V3": "-0.92",
            "V4": "2.44",
            "V7": "1.38",
            "V10": "-1.21",
            "V14": "-1.72",
            "Amount": "1499",
        },
    },
    "unusual_pattern": {
        "label": "Unusual Pattern Transaction",
        "description": "A more unusual anonymized feature profile for showing how the model reacts to abnormal signal combinations.",
        "values": {
            **{column: "0" for column in FEATURE_COLUMNS},
            "Time": "49200",
            "V1": "-3.78",
            "V2": "4.11",
            "V3": "-5.2",
            "V4": "3.88",
            "V5": "-2.44",
            "V7": "-4.18",
            "V9": "-2.03",
            "V10": "-4.72",
            "V11": "3.11",
            "V12": "-5.14",
            "V14": "-6.21",
            "V16": "-3.38",
            "V17": "-5.42",
            "Amount": "752",
        },
    },
}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Administrator access is required.", "error")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)

    return wrapped


@app.context_processor
def inject_layout_context():
    return {
        "current_username": session.get("username"),
        "current_role": session.get("role"),
    }


@app.get("/health")
def health():
    checks = get_app_health(username=session.get("username"))
    summary = health_summary(checks)
    status_code = 200 if summary["status"] == "ok" else 503
    return {
        "status": summary["status"],
        "message": summary["message"],
        "checks": checks,
    }, status_code


def score_demo_transaction(demo):
    values = [float(demo["values"][column]) for column in FEATURE_COLUMNS]
    model = load_model()
    scaler = load_scaler()
    prediction, probability = predict_transaction(model, scaler, values)
    probability_percent = probability_to_percentage(probability)
    risk_level = get_risk_level(probability)
    return {
        "label": demo["label"],
        "description": demo["description"],
        "prediction": get_prediction_text(prediction),
        "probability": probability_percent,
        "risk_level": risk_level,
        "recommendation": get_recommendation(probability),
        "assessment": get_transaction_assessment(
            prediction=prediction,
            probability=probability,
            amount=float(demo["values"]["Amount"]),
            risk_level=risk_level,
        ),
    }


def demo_batch_dataframe():
    rows = []
    for key, demo in DEMO_TRANSACTIONS.items():
        row = {column: float(demo["values"][column]) for column in FEATURE_COLUMNS}
        row["DemoName"] = demo["label"]
        rows.append(row)
    return pd.DataFrame(rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "register":
            username = request.form.get("username", "")
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            success, message = register_account(username, email, password)
            if success:
                session["logged_in"] = True
                session["username"] = normalize_username(username)
                session["role"] = "user"
                flash("Account created and signed in.", "success")
                return redirect(url_for("dashboard"))

            flash(message, "error")
            return redirect(url_for("login"))

        user = authenticate(
            request.form.get("username", ""),
            request.form.get("password", ""),
        )
        if user is None:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

        session["logged_in"] = True
        session["username"] = user["username"]
        session["role"] = user["role"]
        flash("Login successful.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html", title="Login")


@app.get("/logout")
def logout():
    session.clear()
    flash("Signed out.", "success")
    return redirect(url_for("login"))


@app.get("/")
@login_required
def dashboard():
    username = session["username"]
    stats = get_dashboard_stats()
    summary = summarize_user_history(username)
    checks = get_app_health(username=username)
    readiness = health_summary(checks)
    return render_template(
        "dashboard.html",
        title="Dashboard",
        stats=stats,
        summary=summary,
        readiness=readiness,
        checks=checks,
    )


@app.get("/demo")
def demo():
    try:
        scored_demos = [score_demo_transaction(demo) for demo in DEMO_TRANSACTIONS.values()]
    except Exception as exc:
        scored_demos = []
        flash(f"Demo scoring failed: {exc}", "error")

    return render_template(
        "demo.html",
        title="Public Demo",
        demos=scored_demos,
    )


@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    form_values = {column: "0" for column in FEATURE_COLUMNS}
    form_values["Amount"] = "100"
    selected_demo = request.args.get("demo")
    demo_info = None
    if request.method == "GET" and selected_demo in DEMO_TRANSACTIONS:
        demo_info = DEMO_TRANSACTIONS[selected_demo]
        form_values.update(demo_info["values"])

    result = None

    if request.method == "POST":
        form_values.update({column: request.form.get(column, "0") for column in FEATURE_COLUMNS})

        try:
            input_data = [float(form_values[column]) for column in FEATURE_COLUMNS]
            model = load_model()
            scaler = load_scaler()
            prediction, probability = predict_transaction(model, scaler, input_data)
        except Exception as exc:
            flash(f"Prediction failed: {exc}", "error")
            return render_template(
                "predict.html",
                title="Predict",
                feature_columns=FEATURE_COLUMNS,
                form_values=form_values,
                result=None,
            )

        prediction_text = get_prediction_text(prediction)
        risk_level = get_risk_level(probability)
        recommendation = get_recommendation(probability)
        probability_percent = probability_to_percentage(probability)
        transaction_id = str(uuid.uuid4())[:8]
        amount = float(form_values["Amount"])

        save_prediction(
            username=session["username"],
            transaction_id=transaction_id,
            prediction=prediction_text,
            probability=probability_percent,
            amount=amount,
            risk_level=risk_level,
        )

        result = {
            "transaction_id": transaction_id,
            "prediction": prediction_text,
            "probability": probability_percent,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "assessment": get_transaction_assessment(
                prediction=prediction,
                probability=probability,
                amount=amount,
                risk_level=risk_level,
            ),
        }

    return render_template(
        "predict.html",
        title="Predict",
        feature_columns=FEATURE_COLUMNS,
        form_values=form_values,
        demo_transactions=DEMO_TRANSACTIONS,
        demo_info=demo_info,
        result=result,
    )


@app.route("/batch", methods=["GET", "POST"])
@login_required
def batch():
    result = None

    if request.method == "POST":
        uploaded_file = request.files.get("csv_file")
        if uploaded_file is None or uploaded_file.filename == "":
            flash("Upload a CSV file.", "error")
            return redirect(url_for("batch"))

        try:
            df = pd.read_csv(uploaded_file)
            model = load_model()
            scaler = load_scaler()
            results, predictions, _ = predict_batch(model, scaler, df)
        except Exception as exc:
            flash(f"Batch prediction failed: {exc}", "error")
            return redirect(url_for("batch"))

        total = len(results)
        fraud = int((predictions == 1).sum())
        genuine = int((predictions == 0).sum())
        fraud_rate = round((fraud / total) * 100, 2) if total else 0

        conn = get_connection()
        conn.execute(
            """
            INSERT INTO batch_predictions(username, filename, total, fraud, genuine, fraud_rate)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session["username"],
                uploaded_file.filename,
                total,
                fraud,
                genuine,
                fraud_rate,
            ),
        )
        conn.commit()
        conn.close()

        csv_text = results.to_csv(index=False)
        result = {
            "filename": uploaded_file.filename,
            "total": total,
            "fraud": fraud,
            "genuine": genuine,
            "fraud_rate": fraud_rate,
            "assessment": get_batch_assessment(total, fraud, genuine, fraud_rate),
            "rows": results.head(50).to_dict(orient="records"),
            "columns": list(results.columns),
            "csv_data_uri": "data:text/csv;charset=utf-8," + quote(csv_text),
        }

    return render_template("batch.html", title="Batch", result=result)


@app.route("/analytics", methods=["GET", "POST"])
@login_required
def analytics():
    metrics = None
    top_fraud = []
    preview = []

    if request.method == "POST":
        uploaded_file = request.files.get("csv_file")
        if uploaded_file is None or uploaded_file.filename == "":
            flash("Upload a labeled CSV file.", "error")
            return redirect(url_for("analytics"))

        try:
            df = pd.read_csv(uploaded_file)
            if "Class" not in df.columns:
                raise ValueError("Dataset must contain a Class column.")
            if "Amount" not in df.columns:
                raise ValueError("Dataset must contain an Amount column.")
        except Exception as exc:
            flash(f"Analytics failed: {exc}", "error")
            return redirect(url_for("analytics"))

        total = len(df)
        fraud = int((df["Class"] == 1).sum())
        genuine = int((df["Class"] == 0).sum())
        metrics = {
            "total": total,
            "fraud": fraud,
            "genuine": genuine,
            "fraud_rate": round((fraud / total) * 100, 3) if total else 0,
            "total_amount": round(float(df["Amount"].sum()), 2),
            "average_amount": round(float(df["Amount"].mean()), 2) if total else 0,
        }
        top_fraud = (
            df[df["Class"] == 1]
            .sort_values("Amount", ascending=False)
            .head(20)
            .to_dict(orient="records")
        )
        preview = df.head(10).to_dict(orient="records")

    return render_template(
        "analytics.html",
        title="Analytics",
        metrics=metrics,
        preview=preview,
        top_fraud=top_fraud,
    )


@app.get("/history")
@login_required
def history():
    rows = [dict(row) for row in get_user_history(session["username"])]
    return render_template("history.html", title="History", rows=rows)


@app.get("/profile")
@login_required
def profile():
    username = session["username"]
    user = get_user_profile(username)
    summary = summarize_user_history(username)
    rows = [dict(row) for row in get_user_history(username)[:10]]
    return render_template(
        "profile.html",
        title="Profile",
        user=user,
        summary=summary,
        rows=rows,
    )


@app.get("/admin")
@admin_required
def admin():
    users = [dict(row) for row in get_all_users()]
    logs = [dict(row) for row in get_all_predictions()]
    stats = get_dashboard_stats()
    return render_template(
        "admin.html",
        title="Admin",
        users=users,
        logs=logs,
        stats=stats,
    )


@app.route("/assistant", methods=["GET", "POST"])
@login_required
def assistant():
    response = None
    checks = None
    summary = None
    admin_stats = None
    model_result = None
    prompt = ""

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        intent = detect_app_intent(prompt)

        if intent is None:
            response = "Tell me what you want to do in SecurePay AI."
        elif intent["type"] == "navigate":
            endpoint = ROUTES.get(intent["page"])
            if endpoint == "admin" and session.get("role") != "admin":
                flash("Admin access is required.", "error")
            elif endpoint:
                return redirect(url_for(endpoint))
        elif intent["type"] == "health_check":
            checks = get_app_health(username=session["username"])
            response = health_summary(checks)["message"]
        elif intent["type"] == "history_report":
            return redirect(url_for("download_audit_report"))
        elif intent["type"] == "admin_summary":
            if session.get("role") != "admin":
                flash("Admin access is required.", "error")
            else:
                admin_stats = get_dashboard_stats()
        elif intent["type"] == "model_smoke_test":
            try:
                model = load_model()
                scaler = load_scaler()
                prediction, probability = predict_transaction(model, scaler, [0.0] * 29 + [100.0])
                model_result = {
                    "prediction": get_prediction_text(prediction),
                    "probability": probability_to_percentage(probability),
                    "risk_level": get_risk_level(probability),
                }
            except Exception as exc:
                flash(f"Model test failed: {exc}", "error")
        elif intent["type"] == "history_summary":
            summary = summarize_user_history(session["username"])
        else:
            response = intent.get("answer") or get_assistant_answer(prompt)

    return render_template(
        "assistant.html",
        title="AI Assistant",
        prompt=prompt,
        response=response,
        checks=checks,
        summary=summary,
        admin_stats=admin_stats,
        model_result=model_result,
    )


@app.get("/audit-report")
@login_required
def download_audit_report():
    rows = get_user_history(session["username"])
    if not rows:
        flash("No prediction history is available for an audit report.", "warning")
        return redirect(url_for("history"))

    try:
        from reports.pdf_generator import generate_history_report

        path = generate_history_report(
            username=session["username"],
            rows=rows,
            summary=summarize_user_history(session["username"]),
        )
    except ModuleNotFoundError as exc:
        flash(f"PDF dependency is missing: {exc.name}", "error")
        return redirect(url_for("history"))

    return send_file(path, as_attachment=True, download_name="SecurePay_AI_Audit_Report.pdf")


@app.get("/about")
def about():
    return render_template("about.html", title="About")


@app.get("/reviewer-guide")
def reviewer_guide():
    return render_template("reviewer_guide.html", title="Reviewer Guide")


@app.get("/presentation-download")
def presentation_download():
    try:
        from reports.pdf_generator import generate_project_presentation_pdf
    except ModuleNotFoundError:
        return send_file(
            "docs/SecurePayAI_Presentation.md",
            as_attachment=True,
            download_name="SecurePayAI_Presentation.md",
        )

    path = generate_project_presentation_pdf()
    return send_file(
        path,
        as_attachment=True,
        download_name="SecurePayAI_Final_Project_Presentation.pdf",
    )


@app.get("/presentation-notes")
def presentation_notes():
    return send_file(
        "docs/SecurePayAI_Presentation.md",
        as_attachment=True,
        download_name="SecurePayAI_Presentation.md",
    )


@app.get("/sample-batch.csv")
def sample_batch_csv():
    df = demo_batch_dataframe()
    csv_df = df[FEATURE_COLUMNS]
    output = StringIO()
    csv_df.to_csv(output, index=False)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=securepay_sample_batch.csv"},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
