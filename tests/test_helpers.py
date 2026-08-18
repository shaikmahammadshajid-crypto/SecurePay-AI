from utils.helpers import (
    get_prediction_text,
    get_recommendation,
    get_risk_level,
    probability_to_percentage,
)


def test_prediction_text_labels():
    assert "Fraud" in get_prediction_text(1)
    assert "Genuine" in get_prediction_text(0)


def test_risk_level_boundaries():
    assert "LOW" in get_risk_level(0.29)
    assert "MEDIUM" in get_risk_level(0.30)
    assert "HIGH" in get_risk_level(0.60)
    assert "CRITICAL" in get_risk_level(0.85)


def test_recommendation_boundaries():
    assert "Approve" in get_recommendation(0.29)
    assert "Monitor" in get_recommendation(0.30)
    assert "verification" in get_recommendation(0.60)
    assert "Block" in get_recommendation(0.85)


def test_probability_to_percentage_rounds():
    assert probability_to_percentage(0.12345) == 12.35
