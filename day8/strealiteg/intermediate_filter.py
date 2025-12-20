import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("Intermediate: Interactive Filtering")
st.markdown("Use the filters to dynamically update the displayed data.")
st.markdown("---")

# 1. Data Generation (Static)
@st.cache_data
def generate_inventory_data():
    data = {
        'Product': [f'Item {i}' for i in range(1, 101)],
        'Category': np.random.choice(['Electronics', 'Apparel', 'Books', 'Home Goods'], 100),
        'Price': np.random.uniform(10.0, 500.0, 100).round(2),
        'Stock': np.random.randint(0, 500, 100)
    }
    return pd.DataFrame(data)

df = generate_inventory_data()

# 2. Initialize Session State for Filters
if 'filters' not in st.session_state:
    st.session_state.filters = {
        'category': df['Category'].unique().tolist(),
        'min_price': df['Price'].min(),
        'max_stock': df['Stock'].max()
    }

# 3. Filter Layout
col1, col2, col3 = st.columns(3)

with col1:
    selected_categories = st.multiselect(
        "Select Categories",
        df['Category'].unique().tolist(),
        default=st.session_state.filters['category'],
        key="cat_select" # Using a key to track widget state
    )
    # Update session state upon change
    st.session_state.filters['category'] = selected_categories

with col2:
    price_range = st.slider(
        "Price Range ($)",
        float(df['Price'].min()), 
        float(df['Price'].max()), 
        (st.session_state.filters['min_price'], df['Price'].max()), # Keep max price the same for simplicity
        step=5.0
    )
    st.session_state.filters['min_price'] = price_range[0]

with col3:
    max_stock_val = st.number_input(
        "Maximum Stock Level",
        min_value=0,
        max_value=int(df['Stock'].max()),
        value=int(st.session_state.filters['max_stock'])
    )
    st.session_state.filters['max_stock'] = max_stock_val

# 4. Apply Filters
filtered_df = df[
    (df['Category'].isin(st.session_state.filters['category'])) &
    (df['Price'] >= st.session_state.filters['min_price']) &
    (df['Stock'] <= st.session_state.filters['max_stock'])
]

st.info(f"Showing {len(filtered_df)} of {len(df)} items.")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# 5. Reset Button
def reset_filters():
    st.session_state.filters = {
        'category': df['Category'].unique().tolist(),
        'min_price': df['Price'].min(),
        'max_stock': df['Stock'].max()
    }

if st.button("Reset All Filters"):
    reset_filters()
    st.rerun()