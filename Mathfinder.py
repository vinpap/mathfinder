import streamlit as st

st.set_page_config(
    page_title="Mathfinder"
)

st.write("# Welcome to Mathfinder! 👋")
st.sidebar.success("Select a page above.")
st.markdown(
    """
    Mathfinder enables you to discover the math that links your data together using AI!

    **👈 Use the sidebar to start using Mathfinder**. Two pages are available:
    - On the 'train' page, you can upload data in CSV format. You will then be asked to define what value in your table you want to predict, and which ones should be used in order to do so. Afterwards, Mathfinder will train an AI model that will give you the math formula linking your data together. The trained model is stored in the app and can be reused to make predictions later. 
    - On the 'predict' page, you can use an already trained model to predict values based on your data. In order to do so, upload a CSV file containing your data and specify the name of the model that should be used. You can download the results in CSV format.

    The app also offers a monitoring function that allows you to ensure the models you trained remain accurate when confronted with new data. 
"""
)