import streamlit as st
# Importing the tool from your existing chatroom file for context
import re
from langchain.tools import tool 

st.set_page_config(layout="wide")

# --- MOCKUP AGENT TOOL (from streamlit_chatroom.py) ---
@tool
def simulated_search(query: str) -> str:
    """Mock tool for demonstration."""
    if "market trends" in query.lower():
        return "Market data suggests a 15% increase in e-commerce adoption."
    return "Simulated search results are general."

# --- PAGE DEFINITIONS ---

def page_home():
    st.header("Welcome to the Multi-Agent Dashboard")
    st.markdown("This application demonstrates a scalable structure for complex projects.")
    
    st.markdown("""
    ### Features:
    - **Dashboard:** High-level metrics (below).
    - **Collaboration:** The multi-agent chat interface.
    """)
    
    # Mock Dashboard Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Agents", "2", "+1 active")
    col2.metric("Tasks Completed", "15", "5 today")
    col3.metric("Last Policy Check", "Vacation Policy", "1 hour ago")

    if st.button("Go to Collaboration Room"):
        st.session_state.page = "collaboration"
        st.rerun()

def page_collaboration_room():
    st.header("Agent Collaboration Room")
    st.markdown("This is where the Analyst and Critic agents meet (mocked here).")
    
    if st.button("Back to Dashboard"):
        st.session_state.page = "home"
        st.rerun()

    # Mock the tool call logic used in your original file
    st.subheader("Simulated Agent Action")
    
    input_query = st.text_input("Agent's Tool Query", value="latest market trends")
    
    if st.button("Run Simulated Search Tool"):
        with st.spinner(f"Running tool: {simulated_search.name}('{input_query}')..."):
            result = simulated_search.func(input_query)
            st.success("Tool Execution Complete!")
            st.code(f"Observation: {result}")
            
# --- MANUAL ROUTER ---

# 1. Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = "home"

# 2. Sidebar Navigation
st.sidebar.title("Navigation")
page_selection = st.sidebar.radio(
    "Go to",
    ["Home", "Collaboration"],
    index=0 if st.session_state.page == "home" else 1
)

# Set session state based on sidebar selection
if page_selection == "Home":
    st.session_state.page = "home"
else:
    st.session_state.page = "collaboration"

# 3. Display the selected page
if st.session_state.page == "home":
    page_home()
elif st.session_state.page == "collaboration":
    page_collaboration_room()