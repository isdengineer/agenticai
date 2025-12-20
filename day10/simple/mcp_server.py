import sys
import json
from mcp.server.fastmcp import FastMCP
import os # Import os for sys.exit call

# 1. Instantiate the MCP Service
mcp_service = FastMCP("EchoService")

@mcp_service.tool()
def echo(message: str) -> str:
    """Takes a string message and returns it back, capitalized."""
    print(f"Server: Executing echo tool on: '{message}'", file=sys.stderr)
    return message.upper()

def run_single_request():
    """Handles a single JSON-RPC request from STDIN and responds to STDOUT."""
    try:
        # Read exactly one line from STDIN
        request_line = sys.stdin.readline().strip()
        if not request_line:
            # If nothing is read, exit cleanly
            return

        request = json.loads(request_line)
        method = request.get("method")
        params = request.get("params", {})
        
        # We only support 'echo' and 'list_tools' for this simple server
        if method == "echo":
            result_data = echo(**params)
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": result_data
            }
        elif method == "list_tools":
            # Manually provide a minimal tool description
            result_data = [{"name": "echo", "description": "echoes input"}]
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": result_data
            }
        else:
            raise NotImplementedError(f"Method '{method}' not implemented.")

        # Write response to STDOUT and IMMEDIATELY flush
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush() 
        
    except Exception as e:
        sys.stderr.write(f"SERVER CRASH ERROR: {e}\n")
        sys.stderr.flush()

if __name__ == "__main__":
    print("MCP Server (Single-Shot) starting...", file=sys.stderr)
    run_single_request()
    # The script exits after processing one request.
    sys.exit(0)