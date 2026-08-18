import numpy as np
import pandas as pd
import pytest

from utils.prediction import FEATURE_COLUMNS, prepare_batch_features, validate_feature_vector


def valid_row():
    return {column: 0.0 for column in FEATURE_COLUMNS}


def test_validate_feature_vector_accepts_30_numeric_features():
    result = validate_feature_vector([0.0] * 30)

    assert result.shape == (1, 30)


def test_validate_feature_vector_rejects_wrong_feature_count():
    with pytest.raises(ValueError, match="Expected 30 features"):
        validate_feature_vector([0.0] * 29)


def test_validate_feature_vector_rejects_nan_and_negative_amount():
    values = [0.0] * 30
    values[5] = np.nan

    with pytest.raises(ValueError, match="NaN or infinite"):
        validate_feature_vector(values)

    values = [0.0] * 30
    values[-1] = -1

    with pytest.raises(ValueError, match="Amount cannot be negative"):
        validate_feature_vector(values)


def test_prepare_batch_features_reorders_and_drops_class():
    row = valid_row()
    row["Class"] = 1
    df = pd.DataFrame([row])

    result = prepare_batch_features(df)

    assert list(result.columns) == FEATURE_COLUMNS
    assert "Class" not in result.columns


def test_prepare_batch_features_rejects_missing_columns():
    row = valid_row()
    del row["V1"]

    with pytest.raises(ValueError, match="Missing required columns: V1"):
        prepare_batch_features(pd.DataFrame([row]))
