"""
Unit tests written before fixing the bugs reported by issues #1, 2, 3, 4
"""
import pytest
import pandas as pd

import app

@pytest.fixture
def dummy_data():
    dummy_dict = {
        "Price": [
            12,
            15,
            3,
            7
        ],
        "Sales": [
            10000,
            5647,
            124,
            666
        ],
        "Temperature": [
            12.3,
            4,
            6.3,
            5
        ]
    }
    return pd.DataFrame(dummy_dict)

@pytest.fixture
def dummy_data_with_nan():
    dummy_dict = {
        "Price": [
            12,
            15,
            3,
            7
        ],
        "Sales": [
            10000,
            5647,
            pd.NA,
            pd.NA
        ],
        "Temperature": [
            12.3,
            4,
            6.3,
            5
        ]
    }
    return pd.DataFrame(dummy_dict)



def test_several_target_columns(dummy_data):
    """
    Test case written for issue #2.

    Makes sure the app does not crash if the user enters several target column names.
    """
    features = "Temperature"
    targets = "Price;Sales"
    app.find_formula(dummy_data, features, targets)


def test_column_names_splitting(dummy_data):
    """
    Test case written for issue #3.

    Makes sure the app does not crash if there are whitespaces before or after
    the separator defined by the code (a semicolumn).
    """
    features = "Temperature; Price" # Notice the extra white space
    targets = "Sales" 
    app.find_formula(dummy_data, features, targets)


def test_nan_handling(dummy_data_with_nan):
    """
    Test case written for issue #4.

    Checks that the app does not crash if the uploaded csv contains missing or invalid values.
    """
    features = "Temperature;Price"
    targets = "Sales"
    app.find_formula(dummy_data_with_nan, features, targets)

def test_invalid_column_name_handling(dummy_data):
    """
    Makes sure the app does not crash if the user enters invalid column names.

    In that case, the app should display an error message instead of crashing.
    """
    features = "Temperature;Date"
    targets = "Sales"
    app.find_formula(dummy_data, features, targets)
