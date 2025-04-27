import uuid
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.tools import Tool
import os
from flask import Flask, stream_with_context, request, Response, jsonify
from flask_cors import CORS
from agent import SearchAgent, AskHuman
from langgraph.types import Command
from dotenv import load_dotenv
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.tools import Tool
from agent import SearchAgent, AskHuman
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
agents = {}  # Store agents in memory for now (can be replaced by a database)

def create_agent(user_id):
    """Helper function to create a new agent."""
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    search = SerpAPIWrapper(serpapi_api_key=os.getenv("SERP_API_KEY"))

    custom_tool = Tool(
        name="web_search",
        description="Search the web for information",
        func=search.run,
    )

    agent = SearchAgent(config=config, tools=[custom_tool, AskHuman])
    agents[user_id] = agent
    return agent.config

@app.route("/get-agent", methods=["POST"])
def get_agent():
    data = request.get_json()
    user_id = data["user_id"]

    if user_id in agents:
        return jsonify({"status": "success", "message": agents[user_id].config})
    else:
        config = create_agent(user_id)
        return jsonify({"status": "success", "message": config})

@app.route("/answer-question", methods=["POST"])
def answer_question():
    data = request.get_json()
    user_id = data["user_id"]
    user_message = data["user_message"]

    if user_id not in agents:
        return jsonify({"status": "error", "message": "Agent not found. Please start a new session."})

    agent = agents[user_id]
    agent_config = data["config"]

    # Process the user message and get AI response
    result = agent.graph.invoke(
        {"messages": [("user", user_message)]},
        agent_config,
    )

    return jsonify({"status": "success", "message": str(agent.get_chat_history())})

@app.route("/resume-conversation", methods=["POST"])
def resume_conversation():
    data = request.get_json()
    user_id = data["user_id"]
    user_message = data["user_message"]

    if user_id not in agents:
        return jsonify({"status": "error", "message": "Agent not found. Please start a new session."})

    agent = agents[user_id]
    agent_config = data["config"]

    # Resume conversation and get AI response
    result = agent.graph.invoke(
        Command(resume=user_message), 
        agent_config,
    )

    return jsonify({"status": "success", "message": str(agent.get_chat_history())})

if __name__ == "__main__":
    app.run(debug=True)
