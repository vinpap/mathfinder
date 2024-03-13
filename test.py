"""
Unit tests written before fixing the bugs reported by issues #1, 2, 3, 4
"""

import pytest
import pandas as pd
import mlflow

from pages import train

mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")


@pytest.fixture
def dummy_data():
    dummy_dict = {
        "Price": [12, 15, 3, 7, 9, 7, 1, 2, 8],
        "Sales": [10000, 5647, 124, 666, 9, 7, 1, 2, 4],
        "Temperature": [12.3, 4, 6.3, 5, 9, 7, 1, 2, 0],
    }
    return pd.DataFrame(dummy_dict)


@pytest.fixture
def dummy_data_with_nan():
    dummy_dict = {
        "Price": [12, 15, 3, 7, 9, 7, 1, 2],
        "Sales": [10000, 5647, pd.NA, pd.NA, 9, 7, 1, 2],
        "Temperature": [12.3, 4, 6.3, 5, 9, 7, 1, 2],
    }
    return pd.DataFrame(dummy_dict)


def test_several_target_columns(dummy_data):
    """
    Test case written for issue #2.

    Makes sure the app does not crash if the user enters several target column names.
    """
    features = "Temperature"
    targets = "Price;Sales"
    train.find_formula(
        dummy_data,
        features,
        targets,
        model_name="test_several_target_columns_model",
        email="test@test.com",
        testing_frequency=0,
        overwrite=True,
    )


def test_column_names_splitting(dummy_data):
    """
    Test case written for issue #3.

    Makes sure the app does not crash if there are whitespaces before or after
    the separator defined by the code (a semicolumn).
    """
    features = "Temperature; Price"  # Notice the extra white space
    targets = "Sales"
    train.find_formula(
        dummy_data,
        features,
        targets,
        model_name="test_column_names_splitting_model",
        email="test@test.com",
        testing_frequency=0,
        overwrite=True,
    )


def test_nan_handling(dummy_data_with_nan):
    """
    Test case written for issue #4.

    Checks that the app does not crash if the uploaded csv contains missing or invalid values.
    """
    features = "Temperature;Price"
    targets = "Sales"
    train.find_formula(
        dummy_data_with_nan,
        features,
        targets,
        model_name="test_nan_handling_model",
        email="test@test.com",
        testing_frequency=0,
        overwrite=True,
    )


def test_invalid_column_name_handling(dummy_data):
    """
    Makes sure the app does not crash if the user enters invalid column names.

    In that case, the app should display an error message instead of crashing.
    """
    features = "Temperature;Date"
    targets = "Sales"
    train.find_formula(
        dummy_data,
        features,
        targets,
        model_name="test_invalid_column_name_handling_model",
        email="test@test.com",
        testing_frequency=0,
        overwrite=True,
    )
