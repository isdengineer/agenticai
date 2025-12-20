import os
import sys
from mcp.langchain import create_mcp_tool_executor
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.agents import AgentFinish
from langchain_classic.agents import AgentExecutor
from langchain_classic.agents.format_scratchpad import format_to_openai_tool_messages
from langchain_classic.agents.output_parsers import OpenAIToolsAgentOutputParser


# --- 1. Set up Ollama LLM ---
# This connects directly to your local Ollama instance
llm = Ollama(model="llama3")


# --- 2. Create the MCP Tool Executor ---
# This launches the external MCP server (the calculator) and wraps it as a LangChain Tool.
# Note: The MCP server runs as a subprocess.
calculator_executor = create_mcp_tool_executor("npx -y @mcp/calculator@latest")


# --- 3. Define the Prompt and Agent Components ---

# The prompt guides the LLM to use the tool
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a specialized math assistant. You must use the 'calculator' tool for any arithmetic. Do not calculate yourself."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# The tools list contains the single MCP tool
tools = [calculator_executor.tool]

# LangChain uses specific functions to format the history and parse the LLM's output
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"] if "chat_history" in x else [],
    }
    | prompt
    | llm.bind_tools(tools)
    | OpenAIToolsAgentOutputParser()
)

# --- 4. Create the Agent Executor ---
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# --- 5. Run the Agent ---
def run_mcp_agent(query: str):
    print("=" * 60)
    print(f"Executing Query: {query}")
    print("=" * 60)
    
    try:
        # The invoke method runs the full agent loop
        result = agent_executor.invoke({"input": query})
        
        print("\n" + "#" * 30)
        print(f"Final Agent Answer: {result['output']}")
        print("#" * 30)

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Ensure Ollama is running and the necessary dependencies are installed.")


if __name__ == "__main__":
    run_mcp_agent("What is the square root of 576, and what is that result multiplied by 15?")
    # This query will force the LLM to call the calculator tool twice.