import pickle

import streamlit as st
import pandas as pd
from sblearn.models import SymbolicRegressor

st.set_page_config(layout="wide")

left_co, cent_co, last_co = st.columns(3)
with cent_co:
    st.title("Use a trained model to make predictions")

uploaded_file = st.file_uploader(
    label="Upload the CSV file that contains your data here"
)

def predict(dataframe: pd.DataFrame, feature_columns: str, model_name: str):
    """
    Uses the trained model identified by 'model_name' to perform predictions
    on the data stored in the columns 'feature_columns'.
    """
    try:
        with open(f"models/{model_name}.pkl", "rb") as model_file:
            model = pickle.load(model_file)
    
    except FileNotFoundError:
        msg_error = f"No model named '{model_name}' was found."
        st.error(msg_error)
        return False

    X = prepare_data(dataframe, feature_columns)
    if type(X) != bool:
        with st.spinner("The model is predicting values based on the data you uploaded. This might take a few seconds, please do not close this page."):
            y_pred = model.predict(X)

        dataframe["predictions"] = y_pred
        csv = dataframe.to_csv(index=False).encode('utf-8')
        st.info(f"Predictions complete! You can download the data in CSV format below:")
        st.download_button("Download CSV",
                           csv,
                           "predictions.csv",
                           "text/csv",
                           key='download-csv'
                           )


def prepare_data(dataframe: pd.DataFrame, feature_columns: str):
    """
    Retrieves the data in the columns required by the user.
    """
    f_headers = feature_columns.split(";")
    for i in range(len(f_headers)):
        f_headers[i] = f_headers[i].strip()

    
    try:
        X = dataframe[f_headers]
    except KeyError:
        msg_error = "An error occured while retrieving the data from the columns you specified. Make sure you entered the column names properly."
        st.error(msg_error)
        return False, False

    return X
    


if uploaded_file:

    df = pd.read_csv(uploaded_file)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Dropping unnamed columns
    with st.expander("Data preview"):
        st.subheader("Your data (preview might be truncated):")
        st.table(df.head(20))
    feature_column_names = st.text_input(
        label="Enter the names of the columns you want to use to make predictions"
    )
    model_name = st.text_input(
        label="Enter the name of the model you want to use"
    )
    kwargs = {
        "dataframe": df,
        "feature_columns": feature_column_names,
        "model_name": model_name
    }
    st.button(label="Make predictions", on_click=predict, kwargs=kwargs)
