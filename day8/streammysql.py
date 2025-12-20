import streamlit as st
from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

st.set_page_config(page_title="SQL Agent with Ollama", page_icon="🦙")

st.title("🦙 Chat with your MySQL Database")
st.caption("Powered by Ollama (Llama 3) and LangChain")

# --- 1. Sidebar Configuration ---
st.sidebar.header("Database Configuration")

# Pre-filling with the credentials from your snippet
mysql_host = st.sidebar.text_input("Host", value="localhost")
mysql_user = st.sidebar.text_input("User", value="root")
mysql_password = st.sidebar.text_input("Password", value="root", type="password")
mysql_db = st.sidebar.text_input("Database Name", value="mydb")

model_name = st.sidebar.selectbox("Ollama Model", ["llama3", "mistral", "sqlcoder"], index=0)

# --- 2. Initialize Agent (Cached) ---
# We use @st.cache_resource so we only connect to the DB once, not on every user interaction
@st.cache_resource(ttl="2h")
def get_sql_agent(username, password, host, db_name, model):
    # Construct URI
    db_uri = f"mysql+mysqlconnector://{username}:{password}@{host}/{db_name}"
    
    try:
        # Connect to DB
        db = SQLDatabase.from_uri(db_uri)
        
        # Initialize LLM
        llm = ChatOllama(model=model, temperature=0)
        
        # Create Agent
        agent_executor = create_sql_agent(
            llm=llm,
            db=db,
            agent_type="zero-shot-react-description",
            verbose=True,
            handle_parsing_errors=True # Good for local models
        )
        return agent_executor
        
    except Exception as e:
        return None

# Attempt to connect
agent = get_sql_agent(mysql_user, mysql_password, mysql_host, mysql_db, model_name)

if not agent:
    st.error("❌ Could not connect to the database. Please check your settings in the sidebar.")
    st.stop()

# --- 3. Chat Interface ---

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "I am connected to your MySQL database. Ask me anything!"}
    ]

# Display chat messages from history on app rerun
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User Input
if prompt := st.chat_input("Ex: What is the total quantity of products ordered by Charlie Davis?"):
    
    # 1. Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 2. Run the Agent
    with st.chat_message("assistant"):
        # This callback handler displays the "Thoughts" and "SQL Query" in the UI
        st_callback = StreamlitCallbackHandler(st.container())
        
        try:
            response = agent.invoke(
                {"input": prompt},
                {"callbacks": [st_callback]} # Attach the UI callback here
            )
            
            final_answer = response["output"]
            
            # Display result
            st.write(final_answer)
            
            # Add assistant message to history
            
            st.session_state.messages.append({"role": "assistant", "content": final_answer})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")