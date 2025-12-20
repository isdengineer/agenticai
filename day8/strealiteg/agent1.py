import streamlit as st
import numpy as np
import concurrent.futures # For managing threads
import asyncio          # For running the async method
from llama_index.core.tools import FunctionTool
from llama_index.llms.ollama import Ollama
from llama_index.core.agent.workflow.react_agent import ReActAgent

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Ollama Agent Demo", layout="wide")
st.title("🗣️ Conversational Agent with Threading Fix")
st.caption("Requires 'ollama serve' running. Uses ReAct Agent with a calculator tool.")

# --- 1. TOOL DEFINITION ---

def calculate_expression(expression: str) -> float:
    """
    Evaluates a mathematical expression (e.g., '10 + 2' or 'np.sqrt(100)'). 
    Args:
        expression: A string containing the mathematical expression.
    Returns:
        The floating-point result of the expression.
    """
    local_env = {'np': np, "__builtins__": None}
    try:
        # Use eval with restricted scope for safety
        result = eval(expression, local_env)
        return float(result)
    except Exception as e:
        # Return NaN or raise an error the agent can observe
        return float('nan')

calculator_tool = FunctionTool.from_defaults(fn=calculate_expression)

# --- 2. AGENT INITIALIZATION (State Management) ---

if 'agent' not in st.session_state:
    @st.cache_resource(show_spinner="Initializing Ollama Agent...")
    def initialize_agent():
        """Creates and returns the Ollama ReAct Agent."""
        try:
            llm = Ollama(model='mistral', request_timeout=120.0, verbose=False)
            agent = ReActAgent(
                llm=llm, 
                tools=[calculator_tool],
                # Set verbose=True here to see the ReAct thought process in the terminal
                verbose=False 
            )
            return agent
        except Exception as e:
            st.error(f"Failed to connect to Ollama. Ensure 'ollama serve' is running. Error: {e}")
            return None
    
    st.session_state.agent = initialize_agent()
    
# Initialize chat message history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am a calculator agent. Ask me a math problem."}
    ]
    
# --- 3. SYNCHRONOUS WRAPPER FUNCTION (The Threading Fix) ---

def run_async_agent_in_thread(agent, prompt):
    """Executes the agent's async method in a dedicated thread to avoid event loop conflicts."""
    
    # 1. Define the asynchronous task
    async def async_task():
        # Use the asynchronous method
        return await agent.run(prompt)

    # 2. Use a ThreadPoolExecutor to run the asyncio task in a separate thread.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the asyncio.run() function to the thread pool
        future = executor.submit(asyncio.run, async_task())
        # Wait for the result and return it
        return future.result()

# --- 4. DISPLAY HISTORY ---

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# --- 5. EXECUTION LOOP ---

if prompt := st.chat_input("Ask your agent..."):
    
    # --- PROMPT MODIFICATION ---
    # We create an instructional prompt for the agent to ensure tool use.
    agent_prompt = f"Calculate the following expression using the available tool: '{prompt}'. You MUST output the expression in the format required by the tool, like '10 + 2' or 'np.sqrt(100)'."
    
    # Append user's original message to history (for display)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run the agent and display the response
    with st.chat_message("assistant"):
        with st.spinner("Agent is calculating and thinking..."):
            
            if st.session_state.agent is None:
                st.error("Agent failed to initialize. Check Ollama server.")
                st.stop()
                
            # Call the synchronous wrapper function
            try:
                # Pass the modified instructional prompt
                response = run_async_agent_in_thread(st.session_state.agent, agent_prompt) 
                
                st.markdown(response.response)
                
                # Store the response
                st.session_state.messages.append(
                    {"role": "assistant", "content": response.response}
                )
            except Exception as e:
                # Catch-all error for environment/threading issues
                st.error(f"Error during execution. Is 'ollama serve' running? Check your Python environment/dependencies. Error: {e}")