import streamlit as st
# Importing the tool from your existing chatroom file for context
import re
from langchain.tools import tool 
import pandas as pd
st.set_page_config(layout="wide")


# --- PAGE DEFINITIONS ---

def page_todo():
    st.header("Todos page")
    st.markdown("This application demonstrates a scalable structure for complex projects.")
    df = pd.read_json("https://jsonplaceholder.typicode.com/todos")
    st.dataframe(df, hide_index=True)
    
    if st.button("Go to Comments Room"):
        st.session_state.page = "comments"
        st.rerun()

def page_comments():
    st.header("Comments page")
    df = pd.read_json("https://jsonplaceholder.typicode.com/comments")
    st.dataframe(df, hide_index=True)
    if st.button("Back to Todos"):
        st.session_state.page = "todos"
        st.rerun()

            
# --- MANUAL ROUTER ---

# 1. Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = "todos"

# 2. Sidebar Navigation
st.sidebar.title("Navigation")
page_selection = st.sidebar.radio(
    "Go to",
    ["todos", "comments"],
    index=0 if st.session_state.page == "todos" else 1
)

# Set session state based on sidebar selection
if page_selection == "todos":
    st.session_state.page = "todos"
else:
    st.session_state.page = "comments"

# 3. Display the selected page
if st.session_state.page == "todos":
    page_todo()
elif st.session_state.page == "comments":
    page_comments()