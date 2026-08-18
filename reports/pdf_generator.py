from pathlib import Path
from uuid import uuid4
from xml.sax.saxutils import escape

from config import APP_NAME, APP_TITLE, MODEL_NAME, REPORTS_DIR


def _reportlab():
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    return colors, letter, getSampleStyleSheet, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _safe_text(value):
    text = "" if value is None else str(value)
    text = text.encode("ascii", "ignore").decode("ascii")
    return escape(text)


def _safe_filename(value):
    text = str(value).strip().lower()
    safe = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in text)
    return safe or "securepay"


def _report_path(prefix, username):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR / f"{_safe_filename(username)}_{prefix}_{uuid4().hex[:10]}.pdf"


def _base_doc(filename):
    colors, letter, get_styles, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle = _reportlab()
    doc = SimpleDocTemplate(str(filename), pagesize=letter, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = get_styles()
    elements = [
        Paragraph(f"<b>{APP_NAME}</b>", styles["Title"]),
        Paragraph(APP_TITLE, styles["Heading2"]),
        Spacer(1, 14),
    ]
    return doc, styles, elements, Paragraph, Spacer, Table, TableStyle, colors


def _key_value_table(items, Table, TableStyle, colors):
    data = [["Field", "Value"]] + [[_safe_text(label), _safe_text(value)] for label, value in items]
    table = Table(data, hAlign="LEFT", colWidths=[150, 330])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#182226")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D3DA")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7FAFB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    return table


def generate_prediction_report(username, result, shap_explanation=None):
    filename = _report_path("prediction_report", username)
    doc, styles, elements, Paragraph, Spacer, Table, TableStyle, colors = _base_doc(filename)

    elements.append(Paragraph("<b>Single Transaction Report</b>", styles["Heading2"]))
    elements.append(
        _key_value_table(
            [
                ("User", username),
                ("Transaction ID", result.get("transaction_id")),
                ("Prediction", result.get("prediction_text") or result.get("prediction")),
                ("Fraud Probability", result.get("probability_display") or result.get("probability")),
                ("Risk Level", result.get("risk_level")),
                ("Amount", f"${float(result.get('amount') or 0):,.2f}"),
                ("Timestamp", result.get("created_at") or result.get("timestamp")),
                ("Model", result.get("model_name") or MODEL_NAME),
            ],
            Table,
            TableStyle,
            colors,
        )
    )
    elements.append(Spacer(1, 14))
    elements.append(
        Paragraph(
            "This report is decision-support evidence. It does not guarantee fraud or genuine behavior.",
            styles["BodyText"],
        )
    )

    if shap_explanation and shap_explanation.get("available"):
        elements.append(Spacer(1, 14))
        elements.append(Paragraph("<b>SHAP Feature Attribution</b>", styles["Heading3"]))
        elements.append(Paragraph(_safe_text(shap_explanation.get("technical")), styles["BodyText"]))
        elements.append(Paragraph(_safe_text(shap_explanation.get("simple")), styles["BodyText"]))
        rows = [["Feature", "Input", "SHAP", "Direction"]]
        for item in shap_explanation.get("top_features", [])[:8]:
            rows.append(
                [
                    _safe_text(item["feature"]),
                    _safe_text(item["input_value"]),
                    _safe_text(item["shap_value"]),
                    _safe_text(item["direction"]),
                ]
            )
        table = Table(rows, hAlign="LEFT", colWidths=[90, 90, 90, 210])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#182226")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D3DA")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(table)

    doc.build(elements)
    return filename


def generate_batch_report(df, username, summary=None):
    filename = _report_path("batch_report", username)
    doc, styles, elements, Paragraph, Spacer, Table, TableStyle, colors = _base_doc(filename)

    summary = summary or {}
    elements.append(Paragraph("<b>Batch Prediction Report</b>", styles["Heading2"]))
    elements.append(
        _key_value_table(
            [
                ("User", username),
                ("Total Transactions", summary.get("total", len(df))),
                ("Fraud Transactions", summary.get("fraud", "")),
                ("Genuine Transactions", summary.get("genuine", "")),
                ("Fraud Rate", f"{float(summary.get('fraud_rate') or 0):.2f}%"),
                ("Average Fraud Probability", f"{float(summary.get('average_probability') or 0):.2f}%"),
                ("Model", MODEL_NAME),
            ],
            Table,
            TableStyle,
            colors,
        )
    )
    elements.append(Spacer(1, 14))
    elements.append(
        Paragraph(
            "Batch results contain model classifications and feature attributions are not generated for every row.",
            styles["BodyText"],
        )
    )

    preview_columns = [column for column in ["Time", "Amount", "Prediction", "Fraud Probability", "Risk Level"] if column in df.columns]
    if preview_columns:
        rows = [preview_columns]
        for _, row in df[preview_columns].head(12).iterrows():
            rows.append([_safe_text(row[column]) for column in preview_columns])
        table = Table(rows, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#182226")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D3DA")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(Spacer(1, 14))
        elements.append(Paragraph("<b>Preview Rows</b>", styles["Heading3"]))
        elements.append(table)

    doc.build(elements)
    return filename


def generate_history_report(username, rows, summary, model_info=None):
    filename = _report_path("audit_report", username)
    doc, styles, elements, Paragraph, Spacer, Table, TableStyle, colors = _base_doc(filename)

    elements.append(Paragraph("<b>Prediction History Report</b>", styles["Heading2"]))
    elements.append(
        _key_value_table(
            [
                ("User", username),
                ("Total Predictions", summary.get("total", 0)),
                ("Fraud Predictions", summary.get("fraud", 0)),
                ("Genuine Predictions", summary.get("genuine", 0)),
                ("Average Fraud Probability", f"{float(summary.get('average_probability') or 0):.2f}%"),
                ("Model", (model_info or {}).get("model_name", MODEL_NAME)),
                ("Model Status", (model_info or {}).get("status", "Unknown")),
            ],
            Table,
            TableStyle,
            colors,
        )
    )

    if rows:
        elements.append(Spacer(1, 14))
        elements.append(Paragraph("<b>Recent Predictions</b>", styles["Heading3"]))
        table_rows = [["Created At", "Transaction ID", "Prediction", "Probability", "Amount", "Risk"]]
        for row in rows[:20]:
            table_rows.append(
                [
                    _safe_text(row["created_at"]),
                    _safe_text(row["transaction_id"]),
                    _safe_text(row["prediction"]),
                    f"{float(row['probability'] or 0):.2f}%",
                    f"${float(row['amount'] or 0):,.2f}",
                    _safe_text(row["risk_level"]),
                ]
            )
        table = Table(table_rows, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#182226")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D3DA")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(table)

    elements.append(Spacer(1, 14))
    elements.append(
        Paragraph(
            "SecurePay AI provides model-based decision support. Final fraud decisions require operational review.",
            styles["BodyText"],
        )
    )
    doc.build(elements)
    return filename
