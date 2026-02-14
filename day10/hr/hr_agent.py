import asyncio
import os
import sys
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[os.path.abspath("hr_server.py")],
        env={**os.environ, "PYTHONUNBUFFERED": "1"}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = await session.list_tools()
            tools = [{"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.inputSchema}} for t in mcp_tools.tools]

            # The "Hiring Manager" Prompt
            prompt = ("Find all resumes in the folder. We are looking for an 'AI Engineer' with Python and SQL skills. "
                      "Read each resume. If a candidate is a good match (score > 70), use the tool to add them "
                      "to the MySQL shortlist. Be strict.")

            messages = [{"role": "user", "content": prompt}]
            print("🕵️  Agentic Recruiter is scanning resumes...")
            
            response = ollama.chat(model="mistral", messages=messages, tools=tools, options={'temperature': 0})

            while response.message.tool_calls:
                messages.append(response.message)
                for call in response.message.tool_calls:
                    print(f"🛠️  Action: {call.function.name} for {call.function.arguments.get('name', 'file')}")
                    result = await session.call_tool(call.function.name, call.function.arguments)
                    messages.append({"role": "tool", "content": str(result.content[0].text), "name": call.function.name})
                
                response = ollama.chat(model="mistral", messages=messages, tools=tools, options={'temperature': 0})

            print(f"\n✨ RECRUITMENT SUMMARY:\n{response.message.content}")

if __name__ == "__main__":
    asyncio.run(main())