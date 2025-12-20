# example_client.py
import requests
import json

BRIDGE = "http://localhost:8080/mcp"

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "invoke",
    "params": {
        "model": "llama3",
        "prompt": "Summarize result in single line",
        "tools": ["todos:list"],
        "httpmethod":"get",
        "tool_inputs": {}
    }
}

r = requests.post(BRIDGE, json=payload, timeout=(5,300))
r.raise_for_status()
resp = r.json()
print(json.dumps(resp, indent=2))
