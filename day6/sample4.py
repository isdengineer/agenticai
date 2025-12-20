import requests
from langchain.tools import tool

# --- Configuration ---
INVENTORY_API_BASE_URL = "http://127.0.0.1:5000/inventory" 

@tool
def check_inventory(product_id: str) -> str:
    """
    Checks the inventory level for a product using the local Flask API.
    Input must be the exact product ID string (e.g., 'WH-1000XM5').
    """
    url = f"{INVENTORY_API_BASE_URL}/{product_id}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()
        
        if data.get("status") == "success":
            stock = data.get("stock_level")
            return f"Inventory check for {product_id}: {stock} units in stock."
        elif data.get("status") == "error":
             return f"Inventory check failed: {data.get('message', 'Unknown error.')}"
        else:
             return f"Inventory check received unexpected data: {data}"
             
    except requests.exceptions.RequestException as e:
        return f"ERROR: Could not connect to inventory API. Ensure Flask server is running on port 5000. Details: {e}"


# Example of how you would use this new tool in your agent loop:
# tools = [check_inventory, calculate_shipping_cost] # (Assuming you keep the shipping tool)
# ... create the agent and invoke as before ...

@tool
def calculate_shipping_cost(location: str) -> str:
    """Calculates the shipping cost to a specific location."""
    if "UK" in location:
        return "Standard shipping is $10. Expedited is $25."
    else:
        return "Standard shipping is $20. Expedited is $40."

tools = [check_inventory, calculate_shipping_cost]

# --- 2. Define the Model using ChatOllama ---
# Ensure your Ollama server is running and the model is pulled.
# 'llama3' is used as an example model name.
try:
    model = ChatOllama(model="mistral", temperature=0)
except Exception as e:
    print(f"Error initializing ChatOllama. Is Ollama running and 'llama3' pulled? Error: {e}")
    # You might want to exit or handle this error gracefully in a real application

# --- 3. Create the Agent ---
# The agent framework remains the same, leveraging the ReAct pattern.
agent = create_agent(
    model, 
    tools=tools, 
    # System prompt is crucial for guiding the model's tool usage.
    system_prompt="You are a helpful e-commerce assistant. Use your tools to answer inventory and shipping questions. You must use the tools when relevant."
)

# --- 4. Invoke the Agent (The Agent Loop runs here) ---
user_query = "Is the WH-1000XM5 headphone in stock, and what's the standard shipping cost to the UK?"

print("--- Running Ollama Agent Loop ---")

# The agent loop will interact with the 'llama3' model to decide when and how to use the tools.
try:
    # Use the Agent Executor to invoke the query
    result = agent.invoke({"messages": [{"role": "user", "content": user_query}]})
    
    # The final output is usually the content of the last message in the list
    final_answer = result["messages"][-1].content
    print("\n✅ Final Agent Answer:")
    print(final_answer)

except Exception as e:
    print(f"\n❌ An error occurred during agent execution: {e}")