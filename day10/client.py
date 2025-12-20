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
        "prompt": "List the files returned by the filesystem tool and summarize what they might contain (one-sentence per file). Use only the tool output, do not guess unseen contents.",
        "tools": ["filesystem:list"],
        "tool_inputs": {"filesystem:list": {"path": "C:\\R"}}
    }
}

r = requests.post(BRIDGE, json=payload, timeout=(5,300))
r.raise_for_status()
resp = r.json()
print(json.dumps(resp, indent=2))
