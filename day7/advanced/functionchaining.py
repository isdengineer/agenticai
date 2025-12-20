from langchain_community.chat_models import ChatOllama
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.agents.agent_types import AgentType
from langchain_core.prompts import ChatPromptTemplate
"""
This takes the basic Agent Executor and gives it tools that are designed to work sequentially. This requires the LLM (Ollama) to perform multi-step reasoning and function chaining (using the output of one tool as the input for the next).
"""
# --- A. Define Chained Tools ---
@tool
def load_data_source(file_name: str) -> str:
    """Loads a specified mock file and returns its raw content as a string."""
    if file_name == "sales_data.csv":
        # Raw, unprocessed mock data
        return "TransactionID, Amount, Status\n101, 55.50, New\n102, 120.00, Complete\n103, 55.50, New\n104, 300.00, Complete"
    return "Error: File not found or not supported."

@tool
def calculate_metrics(raw_data_string: str) -> str:
    """
    Analyzes raw, comma-separated data to calculate and return aggregate metrics.
    Only takes the string output from the load_data_source tool.
    """
    lines = raw_data_string.strip().split('\n')
    if not lines or len(lines) < 2:
        return "Error: Data is empty or invalid."
    
    total_revenue = 0.0
    complete_count = 0
    
    for line in lines[1:]: # Skip header
        try:
            _, amount_str, status = line.split(', ')
            amount = float(amount_str)
            total_revenue += amount
            if status == "Complete":
                complete_count += 1
        except Exception:
            continue
            
    return f"Total Transactions: {len(lines) - 1}. Total Revenue: ${total_revenue:.2f}. Completed Orders: {complete_count}"

tools = [load_data_source, calculate_metrics]

# --- B. Agent Setup ---
ollama_llm = ChatOllama(model="llama3", temperature=0)

# Provide clear instructions for chaining
SYSTEM_PROMPT = """
You are a Data Pipeline Analyst. Your task requires two sequential steps:
1. Use the 'load_data_source' tool first to get the raw sales data.
2. Use the 'calculate_metrics' tool with the EXACT output from the first tool to get the final metrics.
3. Only then, provide the final answer.
"""

agent = create_agent(
    ollama_llm, 
    tools=tools, 
    system_prompt=SYSTEM_PROMPT,
    # This agent type is excellent for following multi-step reasoning plans
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True 
)

# --- C. Execute ---
user_query = "Please process the sales_data.csv file and provide a summary of the key metrics."

print(f"\n--- Advanced Chaining Agent System ---")
print(f"User Query: {user_query}")
print("-" * 40)

# The agent must successfully chain: Action(load) -> Observation(data) -> Action(calculate) -> Observation(metrics) -> Final Answer
response = agent.invoke({"messages": [{"role": "user", "content": user_query}]})

print("\n✅ Final Agent Answer:")
print(response["messages"][-1].content)