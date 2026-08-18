import joblib

from utils.prediction import predict_transaction


def test_model_artifacts_load_and_score_sample_transaction():
    model = joblib.load("models/random_forest.pkl")
    scaler = joblib.load("models/scaler.pkl")

    prediction, probability = predict_transaction(model, scaler, [0.0] * 29 + [100.0])

    assert prediction in (0, 1)
    assert 0.0 <= probability <= 1.0
