import subprocess
import json
import uuid
import sys

def call_mcp_tool_sync(method: str, params: dict):
    # CRITICAL: Use the simplified server for this synchronous communication
    server_script = "mcp_server.py" 
    
    # 1. Start the server
    # We use bufsize=1 (line buffering) for better I/O immediacy
    proc = subprocess.Popen(
        [sys.executable, server_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # 2. Build the JSON-RPC request
    request = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,
        "params": params
    }

    # 3. Send request and flush
    request_str = json.dumps(request) + "\n"
    proc.stdin.write(request_str)
    proc.stdin.flush()
    
    # 4. Read response line (This blocks until the server responds and exits)
    response_line = proc.stdout.readline().strip()
    
    # 5. Wait for the server to confirm termination
    proc.wait(timeout=2) 
    
    # 6. Check for errors
    stderr_output = proc.stderr.read().strip()
    if proc.returncode != 0:
        raise Exception(f"Server exited with error code {proc.returncode}. STDERR: {stderr_output}")

    # The server process will now be safely terminated
    proc.terminate()
    
    return response_line


# ------------------------------
# Call the MCP tools (Requires two separate launches of the server)
# ------------------------------
if __name__ == "__main__":
    
    # The asynchronous client performs list_tools() THEN call_tool().
    # We will simulate this by manually running them sequentially.

    try:
        print(">>> 1. Discovering tools (Simulated list_tools call)")
        # Simulating list_tools (which the server handles manually)
        list_tools_res = call_mcp_tool_sync("list_tools", {})
        print(f"[CLIENT] Tools Found: {list_tools_res}")

        print("\n>>> 2. Calling: echo('MCP Success: The final working client!')")
        res1 = call_mcp_tool_sync("echo", {"message": "MCP Success: The final working client!"})
        
        # Parse and print the final result
        json_res = json.loads(res1)
        print(f"[CLIENT] Final Result: {json_res['result']}")

    except Exception as e:
        print("\n" + "=" * 60)
        print("🛑 FATAL CLIENT ERROR 🛑")
        print(f"Error: {e}")
        print("=" * 60)