import time
import requests
import ollama
import json

# --- Configuration ---
ISS_API_URL = "http://api.open-notify.org/iss-now.json"
OLLAMA_MODEL = "mistral" # Use a fast model like llama3 or mistral
POLLING_INTERVAL = 30 # Poll every 30 seconds

# --- Agent Action (Tool) ---
def print_location_alert(summary: str, timestamp: str):
    """Prints a clear, formatted alert based on the agent's summary."""
    print("=" * 60)
    print(f"🛰️  ISS Agent Report at {timestamp}")
    print(f"📍 Location Analysis:\n{summary}")
    print("=" * 60)

# --- Agent Core Logic (Reasoning) ---
def analyze_iss_location(iss_data: dict):
    """
    Sends the real-time ISS coordinates to the Ollama LLM for reasoning
    and translation into a natural language description.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(iss_data['timestamp']))
    
    # Extract coordinates
    latitude = iss_data['iss_position']['latitude']
    longitude = iss_data['iss_position']['longitude']
    
    # 1. Prepare Prompt (Perception to Reasoning)
    system_prompt = (
        "You are an expert geographical analyst. A user will provide you "
        "with the current latitude and longitude of the International Space Station (ISS). "
        "Your task is to analyze these coordinates and return a concise, "
        "single-paragraph description of the *general region* the ISS is currently over "
        "or near. Do not use any extra formatting."
    )
    
    user_message = (
        f"The current ISS position is: "
        f"Latitude: {latitude}, Longitude: {longitude}."
    )

    print(f"[{time.strftime('%H:%M:%S')}] Pinging LLM for geo-analysis...")

    try:
        # 2. Invoke Ollama LLM
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            options={"temperature": 0.1} # Lower temp for factual summary
        )
        
        agent_summary = response['message']['content'].strip()
        
        # 3. Take Action
        print_location_alert(agent_summary, timestamp)
            
    except Exception as e:
        print(f"[ERROR] Ollama/Analysis Failed: {e}")


# --- Polling Loop (Perception) ---
def start_iss_monitor():
    """Continuously polls the ISS API and feeds data to the Agent."""
    print("🚀 Starting ISS Monitoring Agent.")
    print(f"Polling {ISS_API_URL} every {POLLING_INTERVAL} seconds...")

    

    while True:
        try:
            # 1. Poll the Real API
            api_response = requests.get(ISS_API_URL, timeout=15)
            api_response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
            iss_data = api_response.json()

            # 2. Feed Poll Data to Agent Logic
            analyze_iss_location(iss_data)
            
        except requests.exceptions.RequestException as e:
            print(f"[API ERROR] Failed to connect or receive data: {e}")
        except json.JSONDecodeError:
            print("[API ERROR] Could not decode JSON response.")
        except KeyboardInterrupt:
            print("\nAgent stopped by user.")
            break
        
        # Wait for the next poll
        time.sleep(POLLING_INTERVAL)

if __name__ == "__main__":
    start_iss_monitor()