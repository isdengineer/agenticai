import sqlite3
import json
import re
from typing import Dict, List, Any, Callable
from time import sleep

# Try to import requests for the live API call
try:
    import requests
except ImportError:
    requests = None
    print("Warning: 'requests' library not found. Please run 'pip install requests' to use the live Ollama connection.")

# ==========================================
# 1. ADVANCED TOOLS IMPLEMENTATION
# ==========================================

# --- Global Database Connection (Simulating a persistent DB) ---
# In a real app, you would use a proper connection pool.
CONN = sqlite3.connect(':memory:') # Using in-memory DB for this demo

def setup_database():
    """Initializes the mock database with some sample data."""
    cursor = CONN.cursor()
    cursor.execute('''CREATE TABLE employees 
                      (id INTEGER PRIMARY KEY, name TEXT, department TEXT, salary INTEGER, performance_score REAL)''')
    
    data = [
        (1, 'Alice Smith', 'Sales', 85000, 4.8),
        (2, 'Bob Jones', 'Engineering', 120000, 4.5),
        (3, 'Charlie Brown', 'Marketing', 65000, 3.9),
        (4, 'Diana Prince', 'Engineering', 135000, 4.9),
        (5, 'Evan Wright', 'Sales', 82000, 4.1)
    ]
    cursor.executemany('INSERT INTO employees VALUES (?,?,?,?,?)', data)
    CONN.commit()
    print("[System] Database 'company_db' initialized with table 'employees'.")

def run_sql_query(query: str) -> str:
    """
    Tool: Executes a raw SQL query against the internal employee database.
    Useful for answering questions about staff, salaries, or departments.
    
    Args:
        query: The SQL query string to execute (e.g., "SELECT * FROM employees").
    """
    print(f"\n[Tool: SQL Agent] Executing Query: {query}")
    try:
        # Security Note: In production, strictly limit permissions and sanitize inputs!
        cursor = CONN.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Get column names for better formatting
        if cursor.description:
            columns = [description[0] for description in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return json.dumps(result, indent=2)
        else:
            return "Query executed successfully (No rows returned)."
            
    except sqlite3.Error as e:
        return f"SQL Error: {e}"

def fetch_website_content(url: str) -> str:
    """
    Tool: Simulates scraping text content from a specific URL.
    Useful for researching external topics or retrieving news.
    
    Args:
        url: The full URL to fetch.
    """
    print(f"\n[Tool: Web Scraper] Fetching content from: {url}")
    sleep(1) # Simulate network request
    
    # Mock responses for the sandbox environment
    if "techcrunch" in url or "tech-news" in url:
        return """
        TITLE: AI Market Trends 2025
        CONTENT: The market for Agentic AI is projected to triple. 
        Major companies are shifting from Chatbots to Autonomous Agents 
        that can execute complex workflows.
        """
    elif "wikipedia" in url:
        return """
        TITLE: Python (programming language)
        CONTENT: Python is a high-level, general-purpose programming language. 
        Its design philosophy emphasizes code readability.
        """
    else:
        return "Error: 404 Not Found or Access Denied."

def analyze_sentiment(text: str) -> str:
    """
    Tool: Analyzes the sentiment of a given text string.
    Returns a score from -1 (Negative) to 1 (Positive).
    
    Args:
        text: The content to analyze.
    """
    print(f"\n[Tool: Sentiment Analyzer] Processing text...")
    # Simple mock logic for demonstration
    lower_text = text.lower()
    score = 0.0
    if "good" in lower_text or "successful" in lower_text or "growth" in lower_text:
        score += 0.8
    if "bad" in lower_text or "error" in lower_text or "failure" in lower_text:
        score -= 0.8
        
    return json.dumps({"sentiment_score": score, "label": "Positive" if score > 0 else "Negative"})

# Registry of available tools
TOOL_REGISTRY = {
    "run_sql_query": run_sql_query,
    "fetch_website_content": fetch_website_content,
    "analyze_sentiment": analyze_sentiment
}

# ==========================================
# 2. OLLAMA API INTEGRATION (LIVE CALL)
# ==========================================

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral" 

def generate_schema(tools: Dict[str, Callable]) -> str:
    """Creates a JSON schema for the tools to include in the system prompt."""
    schema = []
    for name, func in tools.items():
        doc = func.__doc__.strip().split('\n')
        desc = doc[0].replace("Tool:", "").strip()
        # Very basic regex to find args (Production would use inspect module)
        schema.append(f"- {name}(args): {desc}")
    return "\n".join(schema)

def call_ollama(prompt: str) -> Dict[str, Any]:
    """
    Performs a live network call to the local Ollama instance.
    Requires 'pip install requests' and 'ollama serve' running.
    """
    
    # 1. Construct System Prompt with Tools
    tool_list = generate_schema(TOOL_REGISTRY)
    system_prompt = (
        "You are an Advanced Autonomous Agent.\n"
        "You have access to the following tools:\n"
        f"{tool_list}\n\n"
        "RULES:\n"
        "1. If you need data, output JSON: {\"tool\": \"tool_name\", \"args\": {...}}\n"
        "2. If you have the answer, output JSON: {\"answer\": \"Your text response\"}"
    )
    
    # 2. Prepare Payload
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "format": "json" # Force Ollama to output valid JSON
    }
    
    print(f"[System] Sending request to Ollama ({OLLAMA_MODEL})...")

    # 3. Execute Request
    try:
        if requests is None:
            raise ImportError("Requests library not available.")

        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        # 4. Parse Response
        # Ollama's 'generate' endpoint returns the text in the 'response' key.
        # Since we asked for format='json', this text should be a JSON string.
        response_json = response.json()
        llm_output_text = response_json.get("response", "")
        
        # Parse the inner JSON created by the LLM
        return json.loads(llm_output_text)

    except ImportError:
         print("Error: 'requests' library is missing.")
         return {"answer": "Error: Please install 'requests' to run this agent live."}
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        return {"answer": f"Error: Could not connect to Ollama at {OLLAMA_API_URL}. Is it running?"}
    except json.JSONDecodeError:
        print(f"Error: LLM did not return valid JSON. Output was: {llm_output_text}")
        return {"answer": "Error: Model failed to generate valid JSON."}

# ==========================================
# 3. THE AGENT RUNTIME LOOP
# ==========================================

def run_agent_task(user_request: str):
    print(f"\n{'='*60}")
    print(f"USER REQUEST: {user_request}")
    print(f"{'='*60}")

    # Step 1: LLM Decides what to do
    decision = call_ollama(user_request)

    # Step 2: Tool Execution Loop
    if "tool" in decision:
        tool_name = decision["tool"]
        tool_args = decision["args"]
        
        # Verify tool exists
        if tool_name in TOOL_REGISTRY:
            func = TOOL_REGISTRY[tool_name]
            
            # Execute
            try:
                result = func(**tool_args)
                print(f"[Agent] Tool Output received. Synthesizing final answer...")
                
                # Step 3: Final Synthesis
                # In a full loop, we would send this result BACK to Ollama.
                # For this demo, we just print the result or simple wrapper.
                print(f"\n>> FINAL AGENT RESPONSE:")
                if tool_name == "run_sql_query":
                    print(f"Based on the database, here is the data: {result}")
                elif tool_name == "fetch_website_content":
                    print(f"I found the following article: {result.strip()}")
                elif tool_name == "analyze_sentiment":
                    print(f"The sentiment analysis result is: {result}")
                else:
                    print(f"Tool output: {result}")
                    
            except Exception as e:
                print(f"Error executing tool: {e}")
        else:
            print(f"Error: Agent tried to call unknown tool '{tool_name}'")
            
    elif "answer" in decision:
        print(f"\n>> FINAL AGENT RESPONSE:\n{decision['answer']}")
    else:
        print("\n>> SYSTEM ERROR: Received unexpected format from LLM.")
        print(decision)

# ==========================================
# 4. EXECUTION
# ==========================================

if __name__ == "__main__":
    setup_database()
    
    # Note: These will only work if Ollama is running locally!
    
    # Example 1: Text-to-SQL (The LLM writes the SQL for us)
    run_agent_task("Who has the highest salary in the company?")
    
    # Example 2: Web Research
    run_agent_task("Fetch the latest tech news from tech-news.com")
    
    # Example 3: Analytic Tool
    run_agent_task("Analyze this feedback: The project launch was a huge success and we saw great growth.")
    
    # Example 4: Complex Filtering
    run_agent_task("Show me all employees in the Engineering department.")