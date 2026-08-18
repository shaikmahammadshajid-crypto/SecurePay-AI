import os
from xml.sax.saxutils import escape

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate


def _safe_text(value):
    text = str(value)
    text = text.encode("ascii", "ignore").decode("ascii")
    return escape(text)


def _safe_filename(value):
    text = str(value).strip().lower()
    safe = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in text)
    return safe or "securepay_user"


def generate_prediction_report(
        username,
        prediction,
        probability,
        amount,
        risk_level):

    os.makedirs("reports/generated", exist_ok=True)

    filename = f"reports/generated/{_safe_filename(username)}_report.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b>SecurePay AI</b>", styles["Title"])
    )

    elements.append(
        Paragraph("Credit Card Fraud Detection Report",
                  styles["Heading2"])
    )

    elements.append(
        Paragraph("<br/>", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>User:</b> {_safe_text(username)}",
                  styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Prediction:</b> {_safe_text(prediction)}",
                  styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Fraud Probability:</b> {probability:.2f}%",
                  styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Amount:</b> ${amount}",
                  styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Risk Level:</b> {_safe_text(risk_level)}",
                  styles["BodyText"])
    )

    doc.build(elements)

    return filename

# -------------------------------
# Batch Prediction PDF Report
# -------------------------------
def generate_batch_report(df, username):
    """
    Generate PDF report for batch prediction results.
    """

    os.makedirs("reports/generated", exist_ok=True)

    filename = f"reports/generated/{_safe_filename(username)}_batch_report.pdf"

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b>SecurePay AI</b>", styles["Title"])
    )

    elements.append(
        Paragraph("Batch Prediction Report", styles["Heading2"])
    )

    elements.append(
        Paragraph("<br/>", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>User:</b> {_safe_text(username)}", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Total Transactions:</b> {len(df)}", styles["BodyText"])
    )

    # Count fraud and genuine transactions
    if df["Prediction"].dtype == object:
        fraud = (df["Prediction"] == "Fraud").sum()
        genuine = (df["Prediction"] == "Genuine").sum()
    else:
        fraud = (df["Prediction"] == 1).sum()
        genuine = (df["Prediction"] == 0).sum()

    elements.append(
        Paragraph(f"<b>Fraud Transactions:</b> {fraud}", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Genuine Transactions:</b> {genuine}", styles["BodyText"])
    )

    doc.build(elements)

    return filename


def generate_history_report(username, rows, summary):
    os.makedirs("reports/generated", exist_ok=True)

    filename = f"reports/generated/{_safe_filename(username)}_audit_report.pdf"
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("<b>SecurePay AI</b>", styles["Title"]),
        Paragraph("Prediction Audit Report", styles["Heading2"]),
        Paragraph("<br/>", styles["BodyText"]),
        Paragraph(f"<b>User:</b> {_safe_text(username)}", styles["BodyText"]),
        Paragraph(f"<b>Total Predictions:</b> {summary['total']}", styles["BodyText"]),
        Paragraph(f"<b>Fraud Predictions:</b> {summary['fraud']}", styles["BodyText"]),
        Paragraph(f"<b>Genuine Predictions:</b> {summary['genuine']}", styles["BodyText"]),
        Paragraph(
            f"<b>Average Fraud Probability:</b> {summary['average_probability']:.2f}%",
            styles["BodyText"],
        ),
        Paragraph("<br/>", styles["BodyText"]),
        Paragraph("<b>Recent Predictions</b>", styles["Heading3"]),
    ]

    for row in rows[:10]:
        elements.append(
            Paragraph(
                " - ".join(
                    [
                        _safe_text(row["created_at"]),
                        _safe_text(row["transaction_id"]),
                        _safe_text(row["prediction"]),
                        f"{float(row['probability'] or 0):.2f}%",
                        f"${float(row['amount'] or 0):,.2f}",
                        _safe_text(row["risk_level"]),
                    ]
                ),
                styles["BodyText"],
            )
        )

    doc.build(elements)

    return filename
