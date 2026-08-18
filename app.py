import logging
import os
import hmac
import secrets
from io import StringIO
from pathlib import Path
from uuid import uuid4

import numpy as np
import pandas as pd
from flask import (
    Flask,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from pandas.errors import EmptyDataError

from config import (
    APP_NAME,
    APP_TITLE,
    APP_VERSION,
    FEATURE_COLUMNS,
    MAX_BATCH_ROWS,
    MAX_UPLOAD_MB,
    REPORTS_DIR,
    RISK_THRESHOLDS,
    SECRET_KEY,
    SESSION_COOKIE_SECURE,
)
from database.admin import (
    get_all_predictions,
    get_all_users,
    get_dashboard_stats,
    get_recent_batches,
    get_risk_distribution,
    save_batch_prediction,
    update_user_role,
)
from database.auth import authenticate, normalize_username, register_account
from database.history import (
    decode_features,
    get_prediction_by_id,
    get_prediction_history,
    save_prediction,
)
from database.profile import get_user_profile
from reports.pdf_generator import generate_batch_report, generate_history_report, generate_prediction_report
from utils.app_health import get_app_health, health_summary
from utils.charts import (
    create_amount_distribution_chart,
    create_fraud_distribution_chart,
    create_labeled_dataset_charts,
    create_prediction_trend_chart,
    create_probability_chart,
    create_risk_distribution_chart,
    create_shap_chart,
)
from utils.explainability import explain_transaction
from utils.helpers import batch_assessment, format_probability, get_risk_level
from utils.model_loader import get_model_info, load_model, load_scaler
from utils.prediction import enrich_batch_results, predict_batch, score_transaction


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.update(
    MAX_CONTENT_LENGTH=MAX_UPLOAD_MB * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=SESSION_COOKIE_SECURE,
)


ROUTES = {
    "dashboard": "dashboard",
    "predict": "predict",
    "batch": "batch",
    "analytics": "analytics",
    "history": "history",
    "reports": "reports",
    "profile": "profile",
    "admin": "admin",
    "about": "about",
}


SAMPLE_TRANSACTIONS = {
    "baseline": {
        "label": "Baseline Transaction",
        "description": "A low-signal sample for validating the full prediction workflow.",
        "values": {
            **{column: "0" for column in FEATURE_COLUMNS},
            "Amount": "100",
        },
    },
    "high_amount": {
        "label": "High Amount Transaction",
        "description": "A larger transaction profile for demonstrating probability and risk-band behavior.",
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
        "description": "A high-signal anonymized profile for demonstrating abnormal feature combinations.",
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


def home_for_role(role):
    if role == "admin":
        return "admin"
    return "dashboard"


def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    from functools import wraps

    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Administrator access is required.", "error")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)

    return wrapped


@app.before_request
def protect_forms_from_csrf():
    """Reject cross-site POSTs before they reach a state-changing route."""
    if request.method != "POST":
        return None

    expected_token = session.get("csrf_token")
    submitted_token = request.form.get("csrf_token", "")
    if expected_token and hmac.compare_digest(expected_token, submitted_token):
        return None

    logger.warning("Rejected a form submission with an invalid CSRF token on %s", request.path)
    flash("Your form expired or could not be verified. Please try again.", "error")
    return redirect(request.path)


@app.context_processor
def inject_layout_context():
    csrf_token = session.get("csrf_token")
    if not csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        session["csrf_token"] = csrf_token

    return {
        "app_name": APP_NAME,
        "app_title": APP_TITLE,
        "app_version": APP_VERSION,
        "current_username": session.get("username"),
        "current_role": session.get("role"),
        "current_endpoint": request.endpoint,
        "home_endpoint": home_for_role(session.get("role")) if session.get("logged_in") else "login",
        "risk_thresholds": RISK_THRESHOLDS,
        "feature_columns": FEATURE_COLUMNS,
        "csrf_token": csrf_token,
    }


@app.errorhandler(413)
def upload_too_large(_error):
    flash(f"Upload is too large. Use a CSV under {MAX_UPLOAD_MB} MB.", "error")
    return redirect(request.referrer or url_for("batch"))


@app.errorhandler(404)
def not_found(_error):
    return render_template(
        "error.html",
        title="Page Not Found",
        error_code="404",
        error_title="Page not found",
        error_message="The requested SecurePay AI page does not exist.",
    ), 404


@app.errorhandler(500)
def server_error(error):
    logger.exception("Unhandled application error: %s", error)
    return render_template(
        "error.html",
        title="Server Error",
        error_code="500",
        error_title="Something went wrong",
        error_message="SecurePay AI could not complete this request. Check health status before retrying.",
    ), 500


@app.get("/health")
def health():
    checks = get_app_health(username=session.get("username"))
    summary = health_summary(checks)
    status_code = 200 if summary["status"] == "ok" else 503
    return {"status": summary["status"], "message": summary["message"], "checks": checks}, status_code


def summarize_history(rows):
    rows = [dict(row) for row in rows]
    total = len(rows)
    if total == 0:
        return {
            "total": 0,
            "fraud": 0,
            "genuine": 0,
            "average_probability": 0.0,
            "average_amount": 0.0,
            "latest": "No saved predictions yet.",
        }

    fraud = sum(1 for row in rows if "Fraud" in str(row.get("prediction", "")))
    probabilities = [float(row["probability"]) for row in rows if row.get("probability") is not None]
    amounts = [float(row["amount"] or 0) for row in rows]
    latest = rows[0]
    return {
        "total": total,
        "fraud": fraud,
        "genuine": total - fraud,
        "average_probability": round(sum(probabilities) / len(probabilities), 2) if probabilities else 0.0,
        "average_amount": round(sum(amounts) / len(amounts), 2) if amounts else 0.0,
        "latest": (
            f"{latest.get('transaction_id')} was {latest.get('prediction')} "
            f"at {format_probability(latest.get('probability'))}."
        ),
    }


def sample_batch_dataframe():
    rows = []
    for sample in SAMPLE_TRANSACTIONS.values():
        rows.append({column: float(sample["values"][column]) for column in FEATURE_COLUMNS})
    return pd.DataFrame(rows)


def _read_csv_upload(uploaded_file, label):
    if uploaded_file is None or uploaded_file.filename == "":
        raise ValueError(f"Upload a {label} CSV file.")
    if not uploaded_file.filename.lower().endswith(".csv"):
        raise ValueError("Only .csv files are supported.")

    try:
        return pd.read_csv(uploaded_file)
    except EmptyDataError as exc:
        raise ValueError("The uploaded CSV is empty.") from exc
    except UnicodeDecodeError as exc:
        raise ValueError("The uploaded CSV could not be decoded. Save it as UTF-8 and try again.") from exc
    except Exception as exc:
        raise ValueError("The uploaded CSV could not be read.") from exc


def _generated_name(username, prefix, extension):
    safe_user = normalize_username(username).replace("/", "_") or "securepay"
    return f"{safe_user}_{prefix}_{uuid4().hex[:10]}.{extension}"


def _save_downloads(username, enriched_results, summary):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_name = _generated_name(username, "batch_results", "csv")
    csv_path = REPORTS_DIR / csv_name
    enriched_results.to_csv(csv_path, index=False)

    excel_name = None
    try:
        excel_name = _generated_name(username, "batch_results", "xlsx")
        enriched_results.to_excel(REPORTS_DIR / excel_name, index=False)
    except Exception:
        logger.exception("Excel export failed")
        excel_name = None

    pdf_name = None
    try:
        pdf_path = generate_batch_report(enriched_results, username, summary)
        pdf_name = Path(pdf_path).name
    except Exception:
        logger.exception("Batch PDF export failed")
        pdf_name = None

    return {"csv": csv_name, "excel": excel_name, "pdf": pdf_name}


def _download_url(filename):
    if not filename:
        return None
    return url_for("download_generated_file", filename=filename)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for(home_for_role(session.get("role"))))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "register":
            username = request.form.get("username", "")
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            password_confirmation = request.form.get("password_confirmation", "")
            if password != password_confirmation:
                flash("Passwords do not match.", "error")
                return redirect(url_for("login"))
            success, message = register_account(username, email, password)
            if success:
                session.clear()
                session["logged_in"] = True
                session["username"] = normalize_username(username)
                session["role"] = "user"
                flash("Account created and signed in.", "success")
                return redirect(url_for("dashboard"))

            flash(message, "error")
            return redirect(url_for("login"))

        user = authenticate(request.form.get("username", ""), request.form.get("password", ""))
        if user is None:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

        session.clear()
        session["logged_in"] = True
        session["username"] = user["username"]
        session["role"] = user["role"]
        flash("Login successful.", "success")
        return redirect(url_for(home_for_role(user["role"])))

    return render_template("login.html", title="Login")


@app.get("/logout")
def logout():
    session.clear()
    flash("Signed out.", "success")
    return redirect(url_for("login"))


@app.get("/")
@login_required
def dashboard():
    if session.get("role") == "admin":
        return redirect(url_for("admin"))

    username = session["username"]
    rows = get_prediction_history(username=username, limit=50)
    summary = summarize_history(rows)
    stats = get_dashboard_stats(username=username)
    risk_distribution = get_risk_distribution(username=username)
    charts = {
        "fraud": create_fraud_distribution_chart(rows),
        "risk": create_risk_distribution_chart(risk_distribution),
        "trend": create_prediction_trend_chart(rows),
    }
    checks = get_app_health(username=username)
    return render_template(
        "dashboard.html",
        title="Dashboard",
        stats=stats,
        summary=summary,
        recent_rows=[dict(row) for row in rows[:8]],
        readiness=health_summary(checks),
        checks=checks,
        charts=charts,
    )


@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    form_values = {column: "0" for column in FEATURE_COLUMNS}
    form_values["Amount"] = "100"
    selected_sample = request.args.get("sample")
    sample_info = None
    if request.method == "GET" and selected_sample in SAMPLE_TRANSACTIONS:
        sample_info = SAMPLE_TRANSACTIONS[selected_sample]
        form_values.update(sample_info["values"])

    result = None
    shap_explanation = None
    shap_chart = None

    if request.method == "POST":
        form_values.update({column: request.form.get(column, "0") for column in FEATURE_COLUMNS})
        try:
            model = load_model()
            scaler = load_scaler()
            result = score_transaction(model, scaler, form_values)
            shap_explanation = explain_transaction(model, scaler, result["features"])
            shap_chart = create_shap_chart(shap_explanation.get("top_features"))
            prediction_id = save_prediction(
                username=session["username"],
                transaction_id=result["transaction_id"],
                prediction=result["prediction_text"],
                probability=result["probability_percent"],
                amount=result["amount"],
                risk_level=result["risk_level"],
                model_name=result["model_name"],
                features=result["features"],
            )
            result["prediction_id"] = prediction_id
            result["report_url"] = url_for("prediction_report", prediction_id=prediction_id)
            flash("Transaction analyzed and saved to prediction history.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        except Exception:
            logger.exception("Manual prediction failed")
            flash("Prediction failed. Verify model artifacts and input values, then try again.", "error")

    return render_template(
        "predict.html",
        title="Manual Prediction",
        feature_columns=FEATURE_COLUMNS,
        form_values=form_values,
        sample_transactions=SAMPLE_TRANSACTIONS,
        sample_info=sample_info,
        result=result,
        shap_explanation=shap_explanation,
        shap_chart=shap_chart,
    )


@app.route("/batch", methods=["GET", "POST"])
@login_required
def batch():
    result = None

    if request.method == "POST":
        uploaded_file = request.files.get("csv_file")
        try:
            df = _read_csv_upload(uploaded_file, "batch prediction")
            model = load_model()
            scaler = load_scaler()
            results, predictions, probabilities = predict_batch(model, scaler, df)
            enriched = enrich_batch_results(results, predictions, probabilities)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("batch"))
        except Exception:
            logger.exception("Batch prediction failed")
            flash("Batch prediction failed. Validate the CSV and model artifacts before retrying.", "error")
            return redirect(url_for("batch"))

        total = len(enriched)
        fraud = int((predictions == 1).sum())
        genuine = int((predictions == 0).sum())
        fraud_rate = round((fraud / total) * 100, 2) if total else 0
        finite_probabilities = np.asarray(probabilities, dtype=float)
        finite_probabilities = finite_probabilities[np.isfinite(finite_probabilities)]
        average_probability = round(float(finite_probabilities.mean() * 100), 2) if len(finite_probabilities) else None
        summary = {
            "total": total,
            "fraud": fraud,
            "genuine": genuine,
            "fraud_rate": fraud_rate,
            "average_probability": average_probability or 0,
        }

        save_batch_prediction(
            username=session["username"],
            filename=uploaded_file.filename,
            total=total,
            fraud=fraud,
            genuine=genuine,
            fraud_rate=fraud_rate,
            average_probability=average_probability,
        )
        downloads = _save_downloads(session["username"], enriched, summary)

        result = {
            "filename": uploaded_file.filename,
            **summary,
            "assessment": batch_assessment(total, fraud, genuine, fraud_rate),
            "rows": enriched.head(50).to_dict(orient="records"),
            "columns": list(enriched.columns),
            "download_csv": _download_url(downloads["csv"]),
            "download_excel": _download_url(downloads["excel"]),
            "download_pdf": _download_url(downloads["pdf"]),
        }
        flash("Batch CSV analyzed successfully.", "success")

    return render_template(
        "batch.html",
        title="Batch CSV Prediction",
        result=result,
        max_batch_rows=MAX_BATCH_ROWS,
        max_upload_mb=MAX_UPLOAD_MB,
    )


@app.route("/analytics", methods=["GET", "POST"])
@login_required
def analytics():
    username = None if session.get("role") == "admin" else session["username"]
    rows = get_prediction_history(username=username)
    risk_distribution = get_risk_distribution(username=username)
    stats = get_dashboard_stats(username=username)
    charts = {
        "fraud": create_fraud_distribution_chart(rows),
        "risk": create_risk_distribution_chart(risk_distribution),
        "trend": create_prediction_trend_chart(rows),
        "probability": create_probability_chart(rows),
        "amount": create_amount_distribution_chart(rows),
    }
    uploaded_metrics = None
    uploaded_preview = []
    uploaded_top_fraud = []
    uploaded_charts = {}

    if request.method == "POST":
        uploaded_file = request.files.get("csv_file")
        try:
            df = _read_csv_upload(uploaded_file, "labeled analytics")
            if "Class" not in df.columns:
                raise ValueError("Dataset must contain a Class column.")
            if "Amount" not in df.columns:
                raise ValueError("Dataset must contain an Amount column.")
            df["Class"] = pd.to_numeric(df["Class"], errors="coerce")
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
            if df[["Class", "Amount"]].isnull().values.any():
                raise ValueError("Class and Amount must be numeric and cannot be missing.")
            total = len(df)
            fraud = int((df["Class"] == 1).sum())
            genuine = int((df["Class"] == 0).sum())
            uploaded_metrics = {
                "filename": uploaded_file.filename,
                "total": total,
                "fraud": fraud,
                "genuine": genuine,
                "fraud_rate": round((fraud / total) * 100, 3) if total else 0,
                "total_amount": round(float(df["Amount"].sum()), 2),
                "average_amount": round(float(df["Amount"].mean()), 2) if total else 0,
                "fraud_amount": round(float(df.loc[df["Class"] == 1, "Amount"].sum()), 2),
                "highest_fraud_amount": round(float(df.loc[df["Class"] == 1, "Amount"].max()), 2) if fraud else 0,
            }
            uploaded_top_fraud = (
                df[df["Class"] == 1].sort_values("Amount", ascending=False).head(20).to_dict(orient="records")
            )
            uploaded_preview = df.head(10).to_dict(orient="records")
            uploaded_charts = create_labeled_dataset_charts(df)
            flash("Labeled dataset analytics generated.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        except Exception:
            logger.exception("Analytics upload failed")
            flash("Analytics upload failed. Validate the CSV and try again.", "error")

    return render_template(
        "analytics.html",
        title="Analytics",
        stats=stats,
        rows=[dict(row) for row in rows[:20]],
        charts=charts,
        risk_distribution=risk_distribution,
        model_info=get_model_info(),
        uploaded_metrics=uploaded_metrics,
        uploaded_preview=uploaded_preview,
        uploaded_top_fraud=uploaded_top_fraud,
        uploaded_charts=uploaded_charts,
    )


@app.get("/history")
@login_required
def history():
    username = None if session.get("role") == "admin" else session["username"]
    rows = [dict(row) for row in get_prediction_history(username=username)]
    risk_filter = request.args.get("risk", "").strip().upper()
    prediction_filter = request.args.get("prediction", "").strip().lower()
    if risk_filter:
        rows = [row for row in rows if str(row.get("risk_level", "")).upper() == risk_filter]
    if prediction_filter in {"fraud", "genuine"}:
        rows = [row for row in rows if prediction_filter in str(row.get("prediction", "")).lower()]
    return render_template("history.html", title="Prediction History", rows=rows)


@app.get("/reports")
@login_required
def reports():
    username = None if session.get("role") == "admin" else session["username"]
    rows = [dict(row) for row in get_prediction_history(username=username, limit=20)]
    batches = get_recent_batches(username=username, limit=10)
    summary = summarize_history(get_prediction_history(username=username))
    return render_template(
        "reports.html",
        title="Reports",
        rows=rows,
        batches=batches,
        summary=summary,
        model_info=get_model_info(),
    )


@app.get("/profile")
@login_required
def profile():
    username = session["username"]
    user = get_user_profile(username)
    rows = get_prediction_history(username=username, limit=10)
    return render_template(
        "profile.html",
        title="Profile",
        user=user,
        summary=summarize_history(rows),
        rows=[dict(row) for row in rows],
    )


@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    if request.method == "POST":
        try:
            update_user_role(request.form.get("user_id"), request.form.get("role"))
            flash("User role updated.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        except Exception:
            logger.exception("Admin role update failed")
            flash("Role update failed. Try again after checking the user record.", "error")
        return redirect(url_for("admin"))

    logs = [dict(row) for row in get_all_predictions(limit=100)]
    risk_distribution = get_risk_distribution()
    charts = {
        "fraud": create_fraud_distribution_chart(logs),
        "risk": create_risk_distribution_chart(risk_distribution),
        "trend": create_prediction_trend_chart(logs),
    }
    checks = get_app_health()
    return render_template(
        "admin.html",
        title="Admin Dashboard",
        users=[dict(row) for row in get_all_users()],
        logs=logs,
        stats=get_dashboard_stats(),
        risk_distribution=risk_distribution,
        recent_batches=get_recent_batches(limit=10),
        model_info=get_model_info(),
        checks=checks,
        readiness=health_summary(checks),
        charts=charts,
    )


@app.get("/audit-report")
@login_required
def download_audit_report():
    username = None if session.get("role") == "admin" else session["username"]
    rows = get_prediction_history(username=username)
    if not rows:
        flash("No prediction history is available for a PDF report.", "warning")
        return redirect(url_for("reports"))

    try:
        report_owner = "platform" if session.get("role") == "admin" else session["username"]
        path = generate_history_report(
            username=report_owner,
            rows=rows,
            summary=summarize_history(rows),
            model_info=get_model_info(),
        )
    except ModuleNotFoundError as exc:
        flash(f"PDF dependency is missing: {exc.name}", "error")
        return redirect(url_for("reports"))
    except Exception:
        logger.exception("Audit PDF generation failed")
        flash("PDF report generation failed. Check report dependencies and try again.", "error")
        return redirect(url_for("reports"))

    return send_file(path, as_attachment=True, download_name="SecurePay_AI_Audit_Report.pdf")


@app.get("/reports/prediction/<int:prediction_id>")
@login_required
def prediction_report(prediction_id):
    username = None if session.get("role") == "admin" else session["username"]
    row = get_prediction_by_id(prediction_id, username=username)
    if row is None:
        abort(404)

    shap_explanation = None
    features = decode_features(row)
    if features:
        try:
            shap_explanation = explain_transaction(load_model(), load_scaler(), features)
        except Exception:
            logger.exception("Prediction report SHAP generation failed")

    result = {
        "transaction_id": row["transaction_id"],
        "prediction_text": row["prediction"],
        "probability_display": format_probability(row["probability"]),
        "risk_level": row["risk_level"],
        "amount": row["amount"],
        "created_at": row["created_at"],
        "model_name": row["model_name"],
    }

    try:
        path = generate_prediction_report(row["username"], result, shap_explanation=shap_explanation)
    except ModuleNotFoundError as exc:
        flash(f"PDF dependency is missing: {exc.name}", "error")
        return redirect(url_for("reports"))
    except Exception:
        logger.exception("Prediction PDF generation failed")
        flash("Prediction PDF generation failed. Try again after checking report dependencies.", "error")
        return redirect(url_for("reports"))

    return send_file(path, as_attachment=True, download_name=f"SecurePay_AI_{row['transaction_id']}.pdf")


@app.get("/downloads/<path:filename>")
@login_required
def download_generated_file(filename):
    safe_name = Path(filename).name
    path = REPORTS_DIR / safe_name
    if not path.exists() or not path.is_file():
        abort(404)
    if session.get("role") != "admin":
        expected_prefix = f"{normalize_username(session['username'])}_"
        if not safe_name.startswith(expected_prefix):
            abort(404)
    return send_file(path, as_attachment=True)


@app.get("/about")
def about():
    return render_template("about.html", title="About", model_info=get_model_info())


@app.get("/sample-batch.csv")
def sample_batch_csv():
    output = StringIO()
    sample_batch_dataframe()[FEATURE_COLUMNS].to_csv(output, index=False)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=securepay_sample_batch.csv"},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
