import pickle
import os

import streamlit as st
import pandas as pd
from sblearn.models import SymbolicRegressor

model = SymbolicRegressor()

st.set_page_config(layout="wide")

left_co, cent_co, last_co = st.columns(3)
with cent_co:
    st.title("Mathfinder - Discover the math behind your data!")

uploaded_file = st.file_uploader(
    label="Upload the CSV file that contains your data here"
)

def find_formula(dataframe: pd.DataFrame, feature_columns: str, target_columns: str, model_name: str, overwrite_model: str):
    """
    Uses the model to find the formula that best fits the data.
    """
    if not overwrite_model and os.path.exists(f"models/{model_name}.pkl") and os.path.isfile(f"models/{model_name}.pkl"):
        st.error(f"A model named {model_name} already exists. Tick the box 'overwrite any existing model' in the form below if you want to overwrite it.")
        return

    X, y = prepare_data(dataframe, feature_columns, target_columns)
    if type(X) != bool:
        train_model(X, y)
    

def prepare_data(dataframe: pd.DataFrame, feature_columns: str, target_columns: str):
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

def convert_str_to_latex(formula: str) -> str:
    """
    Converts the formula string into its latex equivalent so it can be displayed.
    """
    characters_to_remove = ("$_")
    latex_formula = formula.replace("*", " \\times ")
    latex_formula = latex_formula.replace("/", " \\div ")
    for c in characters_to_remove:
        latex_formula = latex_formula.replace(c, " ")
    
    return latex_formula
  

def train_model(X, y):
    """
    Trains the model with the data provided by the user.
    """

    # Mapping column names to their variable name in the formula generated by the model
    column_values_mapping = {}
    i = 0
    for column in X.columns:
        column_values_mapping[f"x{i}"] = f"\\textsf{{{column}}}"
        i += 1

    i = 0
    for column in y.columns:
        column_values_mapping[f"y{i}"] = f"\\textsf{{{column}}}"
        i += 1

    left_co, cent_co, last_co = st.columns(3)
    with cent_co:
        with st.spinner("The model is looking for the math formulas that best describe your data. This might take a few minutes, do not close this page"):  
            try:
                model.fit(X, y)
                st.balloons()

            except ValueError:
                # Is there more than one target?
                if len(y.shape) != 1:
                    msg_error = "Mathfinder can only work with one target value at a time. Please spcecify only one target column."
                else:
                    msg_error = "An unknown error occured while processing your data."
                st.error(msg_error)
                return
            
            except TypeError:
                # Issues with nan values
                msg_error = "Your dataset contains some data that cannot be processed. Please ensure it contains only numerical values and make sure no value is missing."
                st.error(msg_error)
                return

    st.info("Your model has been trained! It has found the formula below:")      
    c = st.container()
    for formula in model.formulas:
        for m in column_values_mapping:
            formula = formula.replace(m, column_values_mapping[m])
        latex_formula = convert_str_to_latex(formula)
        c.latex(latex_formula)
    st.info("In order to ensure the best performance for your model, please upload testing data. More info on the homepage.")

    with open(f"models/{model_name}.pkl", "wb") as model_file:
        pickle.dump(model, model_file)

    


if uploaded_file:

    df = pd.read_csv(uploaded_file)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Dropping unnamed columns
    with st.expander("Data preview"):
        st.subheader("Your data (preview might be truncated):")
        st.table(df.head(20))
    feature_column_names = st.text_input(
        label="Enter the names of the features columns, separated by semi-columns (;)"
    )
    target_column_names = st.text_input(
        label="Enter the name of the target column"
    )
    model_name = st.text_input(
        label="Enter the name you want to give to your model"
    )
    overwrite = st.checkbox('Overwrite any existing model')
    kwargs = {
        "dataframe": df,
        "feature_columns": feature_column_names,
        "target_columns": target_column_names,
        "model_name": model_name,
        "overwrite_model": overwrite
    }
    st.button(label="Train the model", on_click=find_formula, kwargs=kwargs)
