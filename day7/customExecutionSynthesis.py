"""
Tool Execution (Custom Logic): The execute_plan function handles parsing the structured plan.

Synthesis (Ollama LLM): The SYNTHESIS_PROMPT and final LLM call combine the plan and observations for a final answer.
"""


from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
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
    print(f"    [Tool Called: check_policy('{topic}')]")
    return policies.get(topic.lower(), f"Policy for '{topic}' not found in the database.")

@tool
def check_employee_status(name: str) -> str:
    """Retrieves basic status information for an employee."""
    statuses = {
        "Alice": "Alice's annual PTO balance is 5 days remaining.",
        "Bob": "Bob is currently on an approved 3-month leave of absence.",
    }
    print(f"    [Tool Called: check_employee_status('{name}')]")
    return statuses.get(name, f"Employee '{name}' not found.")

# List of all available tools
tools = [check_policy, check_employee_status]


# --- B. The Mock Plan (The input to our custom logic) ---
# This simulates the structured output that the Planning LLM would have generated.
MOCK_PLAN = """
1. Tool: check_policy('vacation')
2. Tool: check_employee_status('Alice')
3. Tool: N/A (Synthesize all information gathered into a single answer)
"""

# --- C. Custom Execution Logic (The focus of this example) ---

def execute_plan_and_collect_observations(input_dict: dict) -> dict:
    """
    Parses the structured plan string (from input_dict['plan']) and executes the specified tools.
    """
    plan = input_dict['plan']
    results = {}
    
    # Map tool names to actual functions for execution
    tool_map = {tool.name: tool for tool in tools}

    # Regex to find tool calls in the plan string
    # Matches: 'Tool: tool_name(input)' or 'Tool: N/A(...)'
    # Note: We are specifically targeting the tool name and the argument string inside the parentheses.
    tool_call_regex = r"Tool: (\w+)\((.*)\)"

    print("\n--- Executing Custom Plan Steps ---")
    
    for i, line in enumerate(plan.strip().split('\n')):
        match = re.search(tool_call_regex, line.strip())
        
        if match:
            tool_name = match.group(1).strip()
            args_str = match.group(2).strip().strip("'\"") # Clean up quotes/spaces from arguments
            
            if tool_name == 'N/A':
                print(f"Step {i+1}: Synthesis step identified (No tool executed).")
                continue
            
            if tool_name in tool_map:
                print(f"Step {i+1} RUNNING: {tool_name}('{args_str}')")
                tool_func = tool_map[tool_name]
                
                # Execute the tool and store the observation
                observation = tool_func.invoke(args_str)
                results[f"Observation_{i+1}"] = observation
                print(f"    [Result: {observation[:60]}...]")
            else:
                results[f"Observation_{i+1}"] = f"Error: Tool '{tool_name}' not recognized."
        
    # Prepare the output dictionary for the next step (Synthesis)
    return {"question": input_dict['question'], 
            "original_plan": plan, 
            "tool_observations": "\n".join([f"{k}: {v}" for k, v in results.items()])}

# --- D. Final Synthesis Prompt (Input for the second Ollama call) ---

SYNTHESIS_PROMPT = ChatPromptTemplate.from_template(
    """
    You are a final knowledge synthesizer. Your role is to take the execution results and the original
    question to provide a single, comprehensive, and clear final answer. Do not mention the plan or observations
    in your final output.
    
    ORIGINAL QUESTION: {question}
    
    --- EXECUTION DATA ---
    PLAN: {original_plan}
    TOOL EXECUTION RESULTS:
    {tool_observations}
    
    FINAL ANSWER:
    """
)

# --- E. The LCEL Chain Assembly (Execution -> Synthesis) ---
ollama_llm = ChatOllama(model="llama3", temperature=0)

user_question = "What is Alice's PTO policy and remaining balance?"

# 1. Define the input dictionary for the start of the execution phase
initial_input = {"question": user_question, "plan": MOCK_PLAN}

# 2. Wire the Custom Execution Logic
execution_step = RunnableLambda(execute_plan_and_collect_observations).with_config(run_name="ExecutionStep")

# 3. Wire the Synthesis LLM
synthesis_step = SYNTHESIS_PROMPT | ollama_llm | StrOutputParser().with_config(run_name="SynthesisStep")

# The final chain: Execution output is passed directly as input to Synthesis
final_workflow = execution_step | synthesis_step

# --- F. Execute the Custom Workflow ---

print(f"--- Running Custom Execution and Synthesis Workflow ---")
print(f"Question: {user_question}")

final_answer = final_workflow.invoke(initial_input)

print("\n--- Final Synthesized Answer (from Ollama) ---")
print(final_answer)