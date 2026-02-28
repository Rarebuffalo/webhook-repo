import os
from datetime import datetime
from flask import render_template
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["github_events"]
collection = db["events"]
collection.create_index("timestamp")

@app.route("/")
def home():
    return render_template("index.html")

   

@app.route("/webhook", methods=["POST"])
def webhook():
    event_type = request.headers.get("X-GitHub-Event")
    payload = request.get_json()

    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    document = None

    if event_type == "push":
        document = {
            "request_id": payload["head_commit"]["id"],
            "author": payload["pusher"]["name"],
            "action": "PUSH",
            "from_branch": None,
            "to_branch": payload["ref"].split("/")[-1],
            "timestamp": payload["head_commit"]["timestamp"]
        }

    elif event_type == "pull_request":
        pr = payload["pull_request"]

        # MERGE case
        if pr["merged"]:
            document = {
                "request_id": pr["id"],
                "author": pr["user"]["login"],
                "action": "MERGE",
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": pr["merged_at"]
            }

        # PR opened case
        elif payload["action"] == "opened":
            document = {
                "request_id": pr["id"],
                "author": pr["user"]["login"],
                "action": "PULL_REQUEST",
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": pr["created_at"]
            }

    if document:
        collection.insert_one(document)

    return jsonify({"status": "processed"}), 200



def format_timestamp(ts):
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.strftime("%d %B %Y - %I:%M %p UTC")
    
    
@app.route("/events", methods=["GET"])
def get_events():
    events = list(
        collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(10)
    )

    formatted = []

    for event in events:
        ts = format_timestamp(event["timestamp"])

        if event["action"] == "PUSH":
            message = f'{event["author"]} pushed to {event["to_branch"]} on {ts}'

        elif event["action"] == "PULL_REQUEST":
            message = f'{event["author"]} submitted a pull request from {event["from_branch"]} to {event["to_branch"]} on {ts}'

        elif event["action"] == "MERGE":
            message = f'{event["author"]} merged branch {event["from_branch"]} to {event["to_branch"]} on {ts}'

        formatted.append({"message": message})

    return jsonify(formatted), 200

if __name__ == "__main__":
    app.run(debug=True)
