from langchain_classic.agents import initialize_agent, AgentType, Tool
from langchain_community.llms import Ollama
import requests
import json

# -----------------------------
# 1. Config
# -----------------------------
TOOLS_BASE = "http://localhost:9001/tools"

# -----------------------------
# 2. Tool: filesystem:list
# -----------------------------
def filesystem_list(path: str = "."):
    """List files in a directory."""
    payload = {"path": path}
    r = requests.post(f"{TOOLS_BASE}/filesystem/list", json=payload,timeout=500)
    return r.json()

filesystem_tool = Tool(
    name="filesystem_list",
    func=lambda p="." : json.dumps(filesystem_list(p)),
    description="List files in a directory. Input: path as string."
)

# -----------------------------
# 3. Tool: db:query
# -----------------------------
def db_query(sql: str):
    """Execute a toy SQL query."""
    payload = {"sql": sql}
    r = requests.post(f"{TOOLS_BASE}/db/query", json=payload)
    return r.json()

db_query_tool = Tool(
    name="db_query",
    func=lambda q: json.dumps(db_query(q)),
    description="Run a SQL query. Input: SQL string."
)

# -----------------------------
# 4. LLM (Ollama)
# -----------------------------
llm = Ollama(model="llama3")

# -----------------------------
# 5. Create Agent
# -----------------------------
agent = initialize_agent(
    tools=[filesystem_tool, db_query_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# -----------------------------
# 6. Test the Agent
# -----------------------------
print("Running Agent...\n")

response = agent.run(
    """
    List files in the director 'C:\R' using the filesystem_list tool,
    then query the database to get the users list using db_query,
    and summarize the combined result.
    """
)

print("\n\n=== FINAL RESPONSE ===")
print(response)
