import os
from datetime import date

import streamlit as st
import mysql.connector
import mlflow
from mlflow import MlflowClient
import pandas as pd
from sklearn.metrics import mean_absolute_error


def get_original_metrics(model_name: str) -> float:
    """
    Retrieves and returns the Mean Absolute Error of the model's first run.
    """
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name(f"/{model_name}")
    runs = client.search_runs(experiment.experiment_id, order_by=["end_time"])
    first_run = runs[0].data.to_dictionary()
    return first_run["metrics"]["mean absolute error"]

def update_testing_date(model_name: str):
    """
    Update the last testing date in the database.
    """
    with mysql.connector.connect(
        host="localhost",
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PWD"],
        database="mathfinder"
    ) as db:
        with db.cursor() as c:
            today = date.today()
            query = f"""UPDATE Models SET last_testing_date="{today.strftime('%Y-%m-%d')}" WHERE name="{model_name}";"""
            c.execute(query)
            db.commit()

def test(dataframe: pd.DataFrame, feature_columns: list, target_column: str, model_name: str):
    """
    Computes the MAE for the model identified by 'model_name' using the testing data provided.
    """

    client = MlflowClient()
    model_versions = client.search_model_versions(f"name='{model_name}'")
    last_version = model_versions[0].version
    model_uri = client.get_model_version_download_uri(name=model_name, version=last_version)
    # Reconstituting the model local path
    splitted_uri = model_uri.split("/")[1:]
    model_uri = "mlartifacts/" + "/".join(splitted_uri)
    model = mlflow.pyfunc.load_model(model_uri)

    X_test, y_test = prepare_data(dataframe, feature_columns, target_column)
    if type(X_test) != bool:
        with st.spinner("The model is predicting values based on the data you uploaded. This might take a few seconds, please do not close this page."):
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            original_mae = get_original_metrics(model_name)

        if mae < 1.05 * original_mae:
            msg = f"""Congratulations, your model {model_name} is doing well!\nYour model reached a Mean Absolute Error (MAE) of {mae}, which is under the threshold set at 105% of the MAE obtained after the model was trained for the first time. The original MAE was {original_mae}."""
            st.balloons()
        else:
            msg = f"""Your model failed the test, as its Mean Absolute Error (MAE) reached {mae}, which is over the threshold set at 105% of the MAE obtained after the model was trained for the first time. The original MAE was {original_mae}. It is strongly recommended to retrain your model."""
        st.info(msg)
        update_testing_date(model_name)



def prepare_data(dataframe: pd.DataFrame, feature_columns: list, target_columns: list):
    """
    Retrieves the data in the columns required by the user.
    """
    f_headers = feature_columns.split(";")
    for i in range(len(f_headers)):
        f_headers[i] = f_headers[i].strip()

    t_headers = target_columns.split(";")
    for i in range(len(t_headers)):
        t_headers[i] = t_headers[i].strip()
    
    try:
        X = dataframe[f_headers]
        y = dataframe[t_headers]
    except KeyError:
        msg_error = "An error occured while retrieving the data from the columns you specified. Make sure you entered the column names properly."
        st.error(msg_error)
        return False, False

    return X, y 
    
st.set_page_config(layout="wide")

left_co, cent_co, last_co = st.columns(3)
with cent_co:
    st.title("Test the performance of a model")

uploaded_file = st.file_uploader(
    label="Upload the CSV file that contains your testing data here"
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Dropping unnamed columns
    with st.expander("Data preview"):
        st.subheader("Your data (preview might be truncated):")
        st.table(df.head(20))
    feature_column_names = st.text_input(
        label="Enter the names of the columns you want to use to make predictions"
    )
    target_column_name = st.text_input(
        label="Enter the name of the column where the target variable is stored"
    )
    model_name = st.text_input(
        label="Enter the name of the model you want to use"
    )

    kwargs = {
        "dataframe": df,
        "feature_columns": feature_column_names,
        "model_name": model_name,
        "target_column": target_column_name
    }
    st.button(label="Test the model", on_click=test, kwargs=kwargs)
