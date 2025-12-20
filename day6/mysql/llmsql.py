# --- CORRECTED IMPORTS ---
# Use the specific integration package for Ollama for reliability
from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase
# The main high-level function for creating the agent
from langchain_community.agent_toolkits import create_sql_agent

# The import below is REMOVED because create_sql_agent handles it internally:
# from langchain_community.agent_toolkits.sql import SQLDatabaseToolkit

# --- A. MySQL Connection Configuration ---
# You MUST replace these placeholders with your actual MySQL credentials.
MYSQL_USER = "root" 
MYSQL_PASSWORD = "root" 
MYSQL_HOST = "localhost" 
MYSQL_DB_NAME = "mydb" # Database where the customer_orders table resides

# Construct the standard SQLAlchemy connection URI for MySQL
DB_URI = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB_NAME}"

try:
    # 1. Connect to the MySQL Database
    db = SQLDatabase.from_uri(DB_URI)
    print(f"✅ Successfully initialized connection to MySQL DB: {MYSQL_DB_NAME}")
    
    # 2. Initialize Ollama LLM
    # Use the ChatOllama class from the dedicated langchain_ollama package
    ollama_llm = ChatOllama(model="llama3", temperature=0)

    # 3. Create the SQL Agent
    # We pass the 'db' object directly instead of a manually created 'toolkit'.
    agent_executor = create_sql_agent(
        llm=ollama_llm,
        db=db, # <-- FIX: Pass the SQLDatabase object directly
        agent_type="zero-shot-react-description",
        verbose=True # Important for debugging the generated SQL
    )

    # --- B. Query the Database via the Agent ---
    user_query = "What is the total quantity of all products ordered by Charlie Davis?"

    print(f"\n--- Querying MySQL Database via Ollama Agent ---")
    print(f"User Query: {user_query}")
    
    response = agent_executor.invoke({"input": user_query})
    
    print("\n✅ Final Agent Answer:")
    print(response["output"])
    
except Exception as e:
    print(f"\n❌ ERROR: Could not connect to MySQL or execute the agent.")
    print(f"Please check your MySQL credentials, the database name, and ensure the 'customer_orders' table exists.")
    print(f"Detail: {e}")