import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="centered")
st.title("Simple Data Viewer")
st.markdown("---")

# 1. Data Generation (Static)
@st.cache_data
def load_data():
    # Create mock data with random coordinates and a classification column
    data = pd.read_csv("https://gist.githubusercontent.com/netj/8836201/raw/6f9306ad21398ea43cba4f7d537619d0e07d5ae3/iris.csv")
    data.columns=data.columns.str.replace(".","")
    return data

df = load_data()

# 2. Sidebar Input Widget
st.sidebar.header("Controls")
selected_group = st.sidebar.selectbox(
    "Select Variety to Display",
    df['variety'].unique()
)

# 3. Main Content
st.header(f"Data for variety '{selected_group}'")

# Filter data based on sidebar selection
filtered_df = df[df['variety'] == selected_group]

st.dataframe(filtered_df, use_container_width=True)

# 4. Chart Display
st.subheader("Scatter Plot")
st.scatter_chart(
    filtered_df,
    x='sepallength',
    y='petallength'
)

# 5. Button and Status
if st.button("Refresh Data"):
    st.toast("Data Refreshed!", icon="🔄")