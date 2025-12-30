from flask import Flask, render_template, request, jsonify
from app import init_agent  # Import the agent initialization from your existing app.py
import os

app = Flask(__name__)

# --- Global Agent Initialization ---
# We initialize the agent ONCE when the server starts to save time on every request
print("⏳ Booting up Databricks Agent...")
if not os.path.exists("databricks_usage.db"):
    print("⚠️  Data missing. Running setup...")
    import data_setup
    data_setup.setup_data()

agent_executor = init_agent()
print("✅ Agent is ready to serve!")

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/get", methods=["POST"])
def chat():
    msg = request.form["msg"]
    print(f"User Question: {msg}")
    
    try:
        # Run the agent
        response = agent_executor.invoke({"input": msg})
        output = response['output']
        return jsonify({"response": output})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True, port=8080)