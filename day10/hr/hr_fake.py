import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HR_Static_System")

# Our "Fake" File System
STATIC_RESUMES = {
    "resume_alice.txt": "Alice Smith. Skills: Python, SQL, Agentic AI. Experience: 5 years.",
    "resume_bob.txt": "Bob Jones. Skills: Retail Management, Sales. Experience: 10 years."
}

# Our "Fake" Database
shortlisted_db = []

@mcp.tool()
def list_resumes() -> list:
    """Lists all available resumes."""
    return list(STATIC_RESUMES.keys())

@mcp.tool()
def read_resume(filename: str) -> str:
    """Reads the static content of a resume."""
    return STATIC_RESUMES.get(filename, "Error: File not found.")

@mcp.tool()
def add_to_shortlist(name: str, reasoning: str) -> str:
    """Simulates saving a candidate to a database."""
    candidate = {"name": name, "reasoning": reasoning}
    shortlisted_db.append(candidate)
    # Log to stderr so we can see it in the console without breaking JSON-RPC
    sys.stderr.write(f"\n[DB UPDATE] Added: {name}\n")
    return f"Successfully added {name} to the shortlist."

if __name__ == "__main__":
    mcp.run()