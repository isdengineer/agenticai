import streamlit as st
import pandas as pd


# --- Page Setup ---
st.set_page_config(layout="centered", page_title="Simple Widgets Demo")


# 4. Selectbox (Dropdown Menu)
option = st.selectbox(
    "Choose your favorite fruit:",
    ("",'todos', 'comments','posts')
)
st.write(f"Your selected option is: **{option}**")


# Button - Triggers a re-run of the entire script
#if st.button("Download Report"):
#    st.success("Reports of "+option)
#    df = pd.read_json("https://jsonplaceholder.typicode.com/"+option)
#   st.dataframe(df, hide_index=True)
if option != "":
    st.success("Fetching data")
    df = pd.read_json("https://jsonplaceholder.typicode.com/"+option)
    st.dataframe(df, hide_index=True)
