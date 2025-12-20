import streamlit as st
import random
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import tool

# --- Configuration ---
# Use the same model for both agents to show how system prompts define roles
OLLAMA_MODEL = "llama3" 
MAX_TURNS = 4
AGENT_NAMES = ["Analyst Agent", "Critic Agent"]

# --- 1. Agent Tools ---
@tool
def simulated_search(query: str) -> str:
    """
    Simulates a web search or database lookup based on the query.
    This tool provides external, grounded context for the agents.
    """
    query_lower = query.lower()
    if "market trends" in query_lower:
        return "Market data suggests a 15% increase in e-commerce adoption over the last quarter, driven by Gen Z users. Major risk: rising shipping costs."
    elif "shipping costs" in query_lower:
        return "Shipping costs have increased by 8% year-over-year, impacting margins for small businesses."
    elif "ai adoption" in query_lower:
        return "AI implementation is accelerating in logistics, expected to reduce human error by 40%."
    else:
        return f"Simulated search results for '{query}' are inconclusive or general."

# --- 2. Agent Definitions (LangChain Runnables) ---

def create_agent_chain(name: str, persona: str, llm):
    """Creates a distinct LLM chain for each agent."""
    
    # We combine the system prompt with the tool descriptions for the LLM to use ReAct-like logic
    system_prompt = f"""
    You are the {name}, part of a multi-agent chatroom. Your persona is: "{persona}".
    You are participating in a conversation with the other agent.

    Your goal is to contribute constructively to the current topic based on your persona,
    using the available tools when needed.

    The conversation history is crucial. Review it before speaking. 
    If you need factual data, use the available 'simulated_search' tool.
    
    Available Tools: {simulated_search.name}({simulated_search.args}) - {simulated_search.description}
    """
    
    # The prompt template includes the conversation history and the new message
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{conversation_history}\n\n[NEW TURN from the Other Agent: {new_message}]"),
    ])

    # The Chain: Context -> Prompt -> LLM -> Parser
    chain = (
        chat_prompt 
        | llm 
        | StrOutputParser()
    ).with_config(run_name=f"{name}_Chain")
    
    return chain

# --- 3. Custom Tool Execution and Agent Manager ---

def run_agent_turn(agent_chain, current_history, new_message):
    """Handles an agent's turn, including potential tool use and response generation."""
    
    # Simple tool-use detection for this example: 
    # If the LLM output suggests calling the tool, we simulate the tool call.
    # In a full LangChain Agent Executor, this logic is handled automatically.
    
    # 1. Prepare input for the LLM
    input_text = {
        "conversation_history": "\n".join(current_history),
        "new_message": new_message
    }
    
    # 2. Get the LLM's raw response
    raw_response = agent_chain.invoke(input_text)
    
    # 3. Simple Tool Execution Check (Advanced: Use an AgentExecutor)
    tool_call_match = re.search(r"TOOL_CALL:\s*(\w+)\(['\"](.*?)['\"]\)", raw_response, re.IGNORECASE)
    
    if tool_call_match:
        tool_name = tool_call_match.group(1).strip()
        tool_arg = tool_call_match.group(2).strip()
        
        if tool_name.lower() == simulated_search.name.lower():
            # Execute the tool
            observation = simulated_search(tool_arg)
            
            # Re-run the LLM with the observation added to the context
            rerun_history = current_history + [
                f"[Tool Used: {tool_name}('{tool_arg}')]",
                f"[Tool Observation: {observation}]"
            ]
            
            # The LLM synthesizes the final answer based on the observation
            synthesis_input = {
                "conversation_history": "\n".join(rerun_history),
                "new_message": f"Based on the tool observation, synthesize a final answer to the discussion."
            }
            final_response = agent_chain.invoke(synthesis_input)
            
            return f"[USED TOOL: {tool_name}] {final_response}", observation
            
    # 4. No Tool Call (Direct response)
    return raw_response, None


def simulate_chatroom(initial_prompt: str, llm):
    """
    Manages the multi-turn conversation between the two agents.
    """
    
    # Agent Personas and Chains
    agent_a_name = AGENT_NAMES[0] # Analyst
    agent_a_persona = "A data-driven strategy analyst focused on opportunities and growth metrics."
    agent_a_chain = create_agent_chain(agent_a_name, agent_a_persona, llm)
    
    agent_b_name = AGENT_NAMES[1] # Critic
    agent_b_persona = "A critical risk management specialist focused on potential costs and pitfalls."
    agent_b_chain = create_agent_chain(agent_b_name, agent_b_persona, llm)

    # Initial state
    conversation_history = []
    
    # Randomly assign who starts the conversation
    if random.choice([True, False]):
        current_agent_name, current_chain = agent_a_name, agent_a_chain
        next_agent_name, next_chain = agent_b_name, agent_b_chain
    else:
        current_agent_name, current_chain = agent_b_name, agent_b_chain
        next_agent_name, next_chain = agent_a_name, agent_a_chain

    
    # Start the conversation
    last_message = f"User initiated topic: {initial_prompt}"
    
    st.session_state.history.append({"speaker": "User", "message": initial_prompt})
    
    for turn in range(MAX_TURNS):
        
        # 1. Current Agent Responds
        response_text, tool_observation = run_agent_turn(current_chain, conversation_history, last_message)
        
        # 2. Update History and Streamlit
        conversation_history.append(f"[{current_agent_name}]: {response_text}")
        
        display_message = response_text
        if tool_observation:
            display_message = f"**Tool Observation:** `{tool_observation}`\n\n{display_message}"
        
        st.session_state.history.append({"speaker": current_agent_name, "message": display_message})
        
        # Stop if max turns reached or a final conclusion is reached (simplified)
        if turn == MAX_TURNS - 1:
            break
        
        # 3. Swap roles for the next turn
        current_agent_name, next_agent_name = next_agent_name, current_agent_name
        current_chain, next_chain = next_chain, current_chain
        last_message = response_text

    st.session_state.is_running = False
    st.session_state.history.append({"speaker": "System", "message": "Conversation concluded after 4 turns."})


# --- 4. Streamlit UI Setup ---

# Initialize LLM only once
@st.cache_resource
def get_ollama_llm():
    try:
        return ChatOllama(model=OLLAMA_MODEL, temperature=0.7)
    except Exception as e:
        st.error(f"Failed to initialize Ollama LLM. Is Ollama running and model '{OLLAMA_MODEL}' pulled? Error: {e}")
        return None

llm = get_ollama_llm()

st.set_page_config(page_title="Ollama Multi-Agent Chatroom", layout="wide")
st.title("👥 Ollama Multi-Agent Collaboration")
st.markdown("Two specialized agents (`Analyst` and `Critic`) discuss a topic using local intelligence (`llama3`) and a shared tool (`simulated_search`).")

# Initialize chat history
if 'history' not in st.session_state:
    st.session_state.history = []
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# --- Chat History Display ---
chat_container = st.container(height=500, border=True)

with chat_container:
    for chat in st.session_state.history:
        if chat["speaker"] == "User":
            st.chat_message("user").write(chat["message"])
        elif chat["speaker"] == AGENT_NAMES[0]: # Analyst
            st.chat_message("ai", avatar="📈").write(chat["message"])
        elif chat["speaker"] == AGENT_NAMES[1]: # Critic
            st.chat_message("ai", avatar="🚨").write(chat["message"])
        else:
            st.info(chat["message"])


# --- Input and Controls ---
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Enter a topic for the agents to discuss (e.g., 'Pros and cons of adopting AI in logistics'):",
        disabled=st.session_state.is_running
    )

def start_simulation():
    if user_input and llm:
        st.session_state.history = []
        st.session_state.is_running = True
        with st.spinner("Agents are collaborating..."):
            simulate_chatroom(user_input, llm)
    elif not llm:
        st.error("Cannot start. Ollama LLM failed to initialize.")

with col2:
    st.button("Start Collaboration", on_click=start_simulation, disabled=st.session_state.is_running or not user_input)

# Side panel for console adaptation notes
st.sidebar.header("🛠️ Console Adaptation Notes")
st.sidebar.markdown(
    """
    The core logic (`simulate_chatroom` and `run_agent_turn`) can be extracted and run
    in a console environment.

    1.  Remove all `st.` calls.
    2.  Replace `st.session_state.history.append` with `print(...)`.
    3.  Define `initial_prompt` directly and call `simulate_chatroom(initial_prompt, llm)`.
    """
)
st.sidebar.markdown("---")
st.sidebar.info(f"Ollama Model: `{OLLAMA_MODEL}`")