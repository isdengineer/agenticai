# tools_server.py
from flask import Flask, request, jsonify
import os
import time

app = Flask(__name__)

@app.route("/tools/filesystem/list", methods=["POST"])
def list_files():
    """
    Tool: filesystem:list
    Expects JSON: {"path": "<path>"} (optional)
    """
    data = request.json or {}
    path = data.get("path", ".")
    try:
        files = os.listdir(path)
        result = [{"name": f, "is_dir": os.path.isdir(os.path.join(path, f))} for f in files]
        return jsonify({"ok": True, "files": result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@app.route("/tools/db/query", methods=["POST"])
def db_query():
    """
    Tool: db:query
    A toy DB query simulator to show a stateful/tool result.
    Expects JSON: {"sql": "<query>"}
    """
    data = request.json or {}
    sql = data.get("sql", "").lower()
    # Extremely naive imitation of a DB response
    if "select" in sql:
        time.sleep(0.2)  # simulate latency
        rows = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
        return jsonify({"ok": True, "rows": rows})
    else:
        return jsonify({"ok": False, "error": "unsupported or unsafe query"}), 400

if __name__ == "__main__":
    # Runs on port 9001 by default
    app.run(host="0.0.0.0", port=9001)
