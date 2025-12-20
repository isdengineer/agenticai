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
    data = pd.DataFrame({
        'x': np.random.randn(100),
        'y': np.random.randn(100),
        'group': np.random.choice(['A', 'B', 'C'], 100)
    })
    return data

df = load_data()

# 2. Sidebar Input Widget
st.sidebar.header("Controls")
selected_group = st.sidebar.selectbox(
    "Select Group to Display",
    df['group'].unique()
)

# 3. Main Content
st.header(f"Data for Group '{selected_group}'")

# Filter data based on sidebar selection
filtered_df = df[df['group'] == selected_group]

st.dataframe(filtered_df, use_container_width=True)

# 4. Chart Display
st.subheader("Scatter Plot")
st.scatter_chart(
    filtered_df,
    x='x',
    y='y',
    color='group'
)

# 5. Button and Status
if st.button("Refresh Data"):
    st.toast("Data Refreshed!", icon="🔄")