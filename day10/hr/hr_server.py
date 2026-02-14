import os
import mysql.connector
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HR_System")
db_config = {'host': 'localhost', 'user': 'root', 'password': 'root', 'database': 'hr_system'}

@mcp.tool()
def list_resumes() -> list:
    """Lists all resume files in the directory."""
    return [f for f in os.listdir(".") if f.startswith("resume_")]

@mcp.tool()
def read_resume(filename: str) -> str:
    """Reads the content of a specific resume."""
    with open(filename, "r") as f:
        return f.read()

@mcp.tool()
def add_to_shortlist(name: str, skills: str, score: int, reasoning: str):
    """Inserts a qualified candidate into the MySQL database."""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "INSERT INTO shortlisted_candidates (name, skills, match_score, reasoning) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, skills, score, reasoning))
    conn.commit()
    conn.close()
    return f"Successfully shortlisted {name}."

if __name__ == "__main__":
    mcp.run()