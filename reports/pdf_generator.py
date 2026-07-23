from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.units import inch

import os


def generate_prediction_report(
        username,
        prediction,
        probability,
        amount,
        risk_level):

    os.makedirs("reports/generated", exist_ok=True)

    filename = f"reports/generated/{username}_report.pdf"

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
        Paragraph(f"<b>User:</b> {username}",
                  styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Prediction:</b> {prediction}",
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
        Paragraph(f"<b>Risk Level:</b> {risk_level}",
                  styles["BodyText"])
    )

    doc.build(elements)

    return filename

# -------------------------------
# Batch Prediction PDF Report
# -------------------------------

import pandas as pd


def generate_batch_report(df, username):
    """
    Generate PDF report for batch prediction results.
    """

    os.makedirs("reports/generated", exist_ok=True)

    filename = f"reports/generated/{username}_batch_report.pdf"

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
        Paragraph(f"<b>User:</b> {username}", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Total Transactions:</b> {len(df)}", styles["BodyText"])
    )

    if "Prediction" in df.columns:
        fraud = (df["Prediction"] == "Fraud").sum()
        genuine = (df["Prediction"] == "Genuine").sum()

        elements.append(
            Paragraph(f"<b>Fraud Transactions:</b> {fraud}", styles["BodyText"])
        )

        elements.append(
            Paragraph(f"<b>Genuine Transactions:</b> {genuine}", styles["BodyText"])
        )

    doc.build(elements)

    return filename