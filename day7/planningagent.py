"""
Docstring for day7.planningagent
Planning (Ollama LLM): The LLM uses a dedicated prompt to output a structured plan (e.g., a list of steps).
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import tool
import re

# --- A. Define Tools ---
@tool
def check_policy(topic: str) -> str:
    """Provides specific policy details for a given topic like 'vacation' or 'expense report'."""
    policies = {
        "vacation": "Employees are entitled to 20 days of PTO annually. Requests must be submitted 14 days in advance.",
        "expense report": "All expense reports over $500 must be approved by two managers. Receipts are mandatory.",
        "remote work": "Remote work is limited to three days per week, requiring a signed agreement.",
    }
    return policies.get(topic.lower(), f"Policy for '{topic}' not found in the database.")

@tool
def check_employee_status(name: str) -> str:
    """Retrieves basic status information for an employee."""
    statuses = {
        "Alice": "Alice's annual PTO balance is 5 days remaining.",
        "Bob": "Bob is currently on an approved 3-month leave of absence.",
    }
    return statuses.get(name, f"Employee '{name}' not found.")

tools = [check_policy, check_employee_status]

# --- B. Define the Planning Prompt ---
# The prompt forces the LLM to output a structured, numbered plan.
PLANNING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an expert planning system. Given a user's complex question, break it down into a numbered list of sequential, necessary steps. Each step must clearly state which tool to use and the exact input arguments, or state 'N/A' if no tool is needed. Do NOT execute the plan, just generate the steps.\n\n"
     "Available Tools:\n"
     "- check_policy(topic: str)\n"
     "- check_employee_status(name: str)"
     "\n\nExample Plan:\n1. Tool: check_policy('vacation')\n2. Tool: check_employee_status('Alice')\n3. Tool: N/A (Synthesize and answer)"
    ),
    ("human", "{question}"),
])

# --- C. Custom Execution Logic (The advanced part) ---
def execute_plan(input_dict: dict) -> dict:
    """
    Parses the structured plan (a string) and executes the tools.
    This is the core custom logic of the workflow.
    """
    plan = input_dict['plan']
    results = {}
    
    # Map tool names to actual functions
    tool_map = {tool.name: tool for tool in tools}

    # Regex to find tool calls in the plan string
    # Matches: 'Tool: tool_name(input)' or 'Tool: N/A'
    tool_call_regex = r"Tool: (\w+)\((.*)\)"

    print("\n--- Executing Custom Plan Steps ---")
    
    for i, line in enumerate(plan.split('\n')):
        match = re.search(tool_call_regex, line.strip())
        
        if match:
            tool_name = match.group(1).strip()
            # Clean up arguments (remove quotes, spaces)
            args_str = match.group(2).strip().strip("'\"") 
            
            if tool_name == 'N/A':
                print(f"Step {i+1}: Synthesis step (No tool executed).")
                continue
            
            if tool_name in tool_map:
                print(f"Step {i+1}: Calling {tool_name} with input: '{args_str}'")
                tool_func = tool_map[tool_name]
                
                # Execute the tool and store the observation
                observation = tool_func.invoke(args_str)
                results[f"Observation_{i+1}"] = observation
                print(f"Observation: {observation[:50]}...")
            else:
                results[f"Observation_{i+1}"] = f"Error: Tool '{tool_name}' not recognized."
        
    return {"question": input_dict['question'], 
            "original_plan": plan, 
            "tool_observations": "\n".join([f"{k}: {v}" for k, v in results.items()])}

# --- D. Final Synthesis Prompt ---
SYNTHESIS_PROMPT = ChatPromptTemplate.from_template(
    """
    You are a final synthesizer. Given the original question, the plan, and the execution results, 
    generate a comprehensive final answer.
    
    ORIGINAL QUESTION: {question}
    PLAN: {original_plan}
    TOOL EXECUTION RESULTS:
    {tool_observations}
    
    FINAL ANSWER:
    """
)

# --- E. The Full Custom Chain ---
ollama_llm = ChatOllama(model="llama3", temperature=0)

full_custom_workflow = RunnableSequence(
    # 1. Planning Step: Generate the structured plan
    PLANNING_PROMPT | ollama_llm | StrOutputParser().with_config(run_name="Planning"),
    
    # The output (the plan string) is now the input to the next step (the custom function)
    RunnableLambda(lambda plan: {"question": "What is Alice's PTO policy and remaining balance?", "plan": plan}),
    
    # 2. Execution Step: Execute the custom logic (parses and runs tools)
    RunnableLambda(execute_plan).with_config(run_name="Execution"),
    
    # 3. Synthesis Step: Generate the final answer
    SYNTHESIS_PROMPT | ollama_llm | StrOutputParser().with_config(run_name="Synthesis"),
)

# --- F. Execute the Custom Workflow ---
user_question = "What is Alice's PTO policy and remaining balance?"

print(f"--- Running Custom Planning Agent Workflow ---")
print(f"Question: {user_question}")

final_answer = full_custom_workflow.invoke({"question": user_question})

print("\n--- Final Agent Answer ---")
print(final_answer)