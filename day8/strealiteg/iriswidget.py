import streamlit as st
import pandas as pd


# --- Page Setup ---
st.set_page_config(layout="centered", page_title="IRIS Widgets Demo")
st.title("Streamlit IRIS Showcase 🖼️")


st.markdown("---")

# Button - Triggers a re-run of the entire script
if st.button("Show IRIS"):
    st.success("Showing iris")
   
    df = pd.read_csv("https://gist.githubusercontent.com/netj/8836201/raw/6f9306ad21398ea43cba4f7d537619d0e07d5ae3/iris.csv")
    st.dataframe(df, hide_index=True)
  