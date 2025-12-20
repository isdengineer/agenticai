# bridge_server.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import uvicorn
import json

app = FastAPI()

# Configure these for your environment
OLLAMA_BASE = "http://localhost:11434/api"
MODEL_NAME = "llama3"  # change as appropriate

# A simple local registry mapping logical tool names to HTTP endpoints
TOOL_REGISTRY = {
    "filesystem:list": "http://localhost:9001/tools/filesystem/list",
    "db:query": "http://localhost:9001/tools/db/query",
    "todos:list":"https://jsonplaceholder.typicode.com/todos/1"
}

class MCPInvokeParams(BaseModel):
    model: str | None = None
    prompt: str
    tools: list | None = None
    tool_inputs: dict | None = None  # optional mapping tool_name -> input dict

@app.post("/mcp")
async def mcp_entry(request: Request):
    """
    Minimal JSON-RPC-style entry:
    POST body: { "jsonrpc": "2.0", "id": 1, "method": "invoke", "params": { ... } }
    """
    body = await request.json()
    # Basic validation and extraction
    params = body.get("params", {})
    try:
        p = MCPInvokeParams(**params)
    except Exception as e:
        return {"jsonrpc": "2.0", "id": body.get("id"), "error": {"message": f"invalid params: {e}"}}

    model = p.model or MODEL_NAME
    prompt = p.prompt
    tools = p.tools or []
    tool_inputs = p.tool_inputs or {}

    tool_results = {}

    # 1) Handle tool invocations (synchronous, simple pattern)
    for tool_name in tools:
        endpoint = TOOL_REGISTRY.get(tool_name)
        if not endpoint:
            tool_results[tool_name] = {"ok": False, "error": "tool not registered"}
            continue
        # Get input for tool
        input_payload = tool_inputs.get(tool_name, {})
        try:
            if params.get("httpmethod") == "get":
                r=requests.get(endpoint)
            else:
                r = requests.post(endpoint, json=input_payload, timeout=30)
            r.raise_for_status()
            tool_results[tool_name] = r.json()
        except Exception as exc:
            tool_results[tool_name] = {"ok": False, "error": str(exc)}
    print("tools_ results",tool_results)
    # 2) Build an augmented prompt: include tool outputs (small / trimmed)
    # NOTE: in production you'd sanitize and limit length
    if tool_results:
        augmented = (
            "The model has access to the following tool results (do not assume more than listed):\n\n"
            + json.dumps(tool_results, indent=2) + "\n\n"
            + "Now answer the user's prompt.\n\nUser prompt:\n" + prompt
        )
    else:
        augmented = prompt

    # 3) Call Ollama generate API (stream=false for simplicity)
    gen_payload = {
        "model": model,
        "prompt": augmented,
        "stream": False
    }
    try:
        resp = requests.post(f"{OLLAMA_BASE}/generate", json=gen_payload, timeout=300)
        resp.raise_for_status()
        ollama_resp = resp.json()
    except Exception as exc:
        return {"jsonrpc": "2.0", "id": body.get("id"), "error": {"message": f"ollama error: {exc}"}}

    # 4) Return a JSON-RPC-style response including tool results + model output
    return {
        "jsonrpc": "2.0",
        "id": body.get("id"),
        "result": {
            "tool_results": tool_results,
            "model_response": ollama_resp
        }
    }



@app.post("/mcp1")
async def mcp_entry1(request: Request):
    """
    Minimal JSON-RPC-style entry:
    POST body: { "jsonrpc": "2.0", "id": 1, "method": "invoke", "params": { ... } }
    """
    body = await request.json()
    # Basic validation and extraction
    params = body.get("params", {})
    try:
        p = MCPInvokeParams(**params)
    except Exception as e:
        return {"jsonrpc": "2.0", "id": body.get("id"), "error": {"message": f"invalid params: {e}"}}

    model = p.model or MODEL_NAME
    prompt = p.prompt
    tools = p.tools or []
    tool_inputs = p.tool_inputs or {}

    tool_results = {}

    # 1) Handle tool invocations (synchronous, simple pattern)
    for tool_name in tools:
        endpoint = TOOL_REGISTRY.get(tool_name)
        if not endpoint:
            tool_results[tool_name] = {"ok": False, "error": "tool not registered"}
            continue
        # Get input for tool
        input_payload = tool_inputs.get(tool_name, {})
        try:
            if params.get("httpmethod") == "get":
                r=requests.get(endpoint)
            else:
                r = requests.post(endpoint, json=input_payload, timeout=30)
            r.raise_for_status()
            tool_results[tool_name] = r.json()
        except Exception as exc:
            tool_results[tool_name] = {"ok": False, "error": str(exc)}
    print("tools_ results",tool_results)
    return {
        "jsonrpc": "2.0",
        "id": body.get("id"),
        "result": {
            "tool_results": tool_results
        }
    }


if __name__ == "__main__":
    # dev server
    uvicorn.run(app, host="0.0.0.0", port=8080)
