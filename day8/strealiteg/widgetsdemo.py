import streamlit as st
import pandas as pd
import datetime

# --- Page Setup ---
st.set_page_config(layout="centered", page_title="Simple Widgets Demo")
st.title("Streamlit Widgets Showcase 🖼️")
st.subheader("Interactive Inputs and Outputs")

st.markdown("---")

# --- 1. Input Widgets ---

st.header("1. Input Widgets")

# 1. Text Input (Text Box)
user_name = st.text_input(
    "Enter your name:", 
    "Jane Doe"
)
st.write(f"Hello, **{user_name}**!")

# 2. Slider
age = st.slider(
    "Select your age:", 
    min_value=18, 
    max_value=100, 
    value=30, 
    step=1
)
st.write(f"You selected age: **{age}**")

# 3. Checkbox (Boolean Toggle)
agreement = st.checkbox(
    "I agree to display my selection below.", 
    value=True
)

# 4. Selectbox (Dropdown Menu)
option = st.selectbox(
    "Choose your favorite fruit:",
    ('Apple', 'Banana', 'Cherry', 'Durian')
)
st.write(f"Your favorite fruit is: **{option}**")

# 5. Date Input
date_value = st.date_input(
    "Select a date:",
    datetime.date(2025, 1, 1)
)

st.markdown("---")

# --- 2. Button and Display ---

st.header("2. Button and Conditional Display")

# Button - Triggers a re-run of the entire script
if st.button("Generate Report"):
    st.success("Report Generated! (Script Reran)")
    
    if agreement:
        st.subheader("Report Summary (Agreement Checked)")
        
        # 6. Dataframe Widget
        data = {
            'Attribute': ['Name', 'Age', 'Fruit', 'Date'],
            'Value': [user_name, age, option, date_value]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, hide_index=True)
    else:
        st.warning("Agreement checkbox must be checked to view the summary.")

# 7. Code/JSON Widget
st.subheader("Widget State in JSON")
widget_state = {
    "name": user_name,
    "age": age,
    "agreed": agreement,
    "option": option,
    "date": str(date_value)
}
st.json(widget_state)