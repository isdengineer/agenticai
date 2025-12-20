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

BRIDGE = "http://localhost:8080/mcp"
def callmcp(payload):
    r = requests.post(BRIDGE, json=payload, timeout=(5,300))
    return r.json()

def filesystem_list(path: str = "."):
    """List files in a directory."""


    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "invoke",
        "params": {
            "model": "llama3",
            "prompt": "List the files returned by the filesystem tool and summarize what they might contain (one-sentence per file). Use only the tool output, do not guess unseen contents.",
            "tools": ["filesystem:list"],
            "tool_inputs": {"filesystem:list": {"path": path}}
        }
    }
    return callmcp(payload)

 

filesystem_tool = Tool(
    name="filesystem_list",
    func=lambda p="." : json.dumps(filesystem_list(p)),
    description="List files in a directory. Input: path as string."
)

# -----------------------------
# 3. Tool: db:query
# -----------------------------
def db_query():
      payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "invoke",
        "params": {
            "model": "llama3",
            "prompt": "summarize the result in a single line",
            "tools": ["db:query"],
            "tool_inputs": {"db:query": {"sql": "select"}}
        }
        }
      return callmcp(payload)

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
