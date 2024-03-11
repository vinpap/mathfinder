import streamlit as st

st.set_page_config(
    page_title="Mathfinder"
)

st.write("# Welcome to Mathfinder! 👋")
st.sidebar.success("Select a page above.")
st.markdown(
    """
    Mathfinder enables you to discover the math that links your data together using AI!
    **👈 Use the sidebar to start using Mathfinder. Two pages are available:
    - EXPLIQUER PAGE TRAIN
    - EXPLIQUER PAGE PREDICT

    AJOUTER UN TEXTE QUI EXPLIQUE COMMENT UTILISER L'APP
"""
)