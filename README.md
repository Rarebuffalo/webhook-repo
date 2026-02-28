GitHub Webhook Monitoring System
Overview

This project implements a webhook-based system that listens to GitHub repository events (Push, Pull Request, and Merge), stores only the required information in MongoDB, and displays the latest activity in a clean UI that refreshes every 15 seconds.

The main objective was to receive GitHub webhook events, extract minimal necessary data, store it in a structured format, and render the latest repository activity in the required format.

The complete flow of the application is:

GitHub (action-repo)
→ Webhook Endpoint (Flask)
→ MongoDB
→ UI (polling every 15 seconds)

Two repositories are used in this solution:

action-repo – Used to trigger GitHub events.

webhook-repo – Contains the webhook receiver, database logic, API, and UI.

Repositories
1. action-repo

This repository is used only to generate GitHub events such as:

Push

Pull Request (opened)

Merge (Pull Request merged)

A webhook is configured in this repository to send events to the Flask endpoint.

2. webhook-repo

This repository contains:

Flask webhook receiver

MongoDB integration

Event parsing and filtering logic

REST API endpoint (/events)

A simple UI that polls data every 15 seconds

Tech Stack

Python (Flask)

MongoDB Atlas

PyMongo

HTML and JavaScript (for UI)

Ngrok (used during local development for webhook tunneling)

MongoDB Schema

Only the minimal required fields are stored in MongoDB as per the assignment requirement.

Each document follows this structure:

{
"request_id": "string",
"author": "string",
"action": "PUSH | PULL_REQUEST | MERGE",
"from_branch": "string or null",
"to_branch": "string",
"timestamp": "ISO datetime string"
}

No unnecessary data from the GitHub payload is stored.

Event Handling

The webhook endpoint listens to GitHub events and differentiates between:

Push

Format displayed in UI:

{author} pushed to {to_branch} on {timestamp}

Data extracted:

pusher name

branch

commit id

timestamp

Pull Request (Opened)

Format displayed:

{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}

Data extracted:

PR id

author

source branch

target branch

created_at timestamp

Merge

When a pull request is merged (pull_request.merged == true), it is stored as:

{author} merged branch {from_branch} to {to_branch} on {timestamp}

Timestamp Handling

GitHub sends timestamps in different ISO formats (for example, with Z or with timezone offsets like +05:30).

To handle both formats safely, datetime.fromisoformat() is used instead of strict strptime parsing.

All timestamps are formatted before being sent to the frontend.

API Endpoint

GET /events

This endpoint:

Fetches the latest 10 events

Sorts them by timestamp (newest first)

Formats them into readable messages

Returns the formatted list as JSON

The UI only renders the final message returned by this API.

UI Behavior

The frontend:

Calls /events every 15 seconds using setInterval

Clears old data

Renders the latest formatted messages

Displays repository activity in a clean and minimal layout

Setup Instructions
1. Clone the Repository

git clone <webhook-repo-url>
cd webhook-repo

2. Create Virtual Environment

python -m venv venv
source venv/bin/activate

3. Install Dependencies

pip install -r requirements.txt

4. Configure Environment Variables

Create a .env file in the root directory:

MONGO_URI=your_mongodb_connection_string

Example:

MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/github_events?retryWrites=true&w=majority

Make sure:

The database user has read/write access

Your IP is whitelisted in MongoDB Atlas

5. Run the Application

python app.py

Open in browser:

http://127.0.0.1:5000

GitHub Webhook Configuration

Start ngrok:

ngrok http 5000

Copy the HTTPS forwarding URL.

Go to action-repo → Settings → Webhooks → Add Webhook.

Set:

Payload URL:
https://your-ngrok-url/webhook

Content type:
application/json

Events:

Push

Pull Request

After this, any push, PR, or merge in action-repo will automatically trigger the webhook.

Testing

To test the full flow:

Push a commit to action-repo.

Create a Pull Request.

Merge the Pull Request.

Within 15 seconds, the new event will appear in the UI.

Implementation Notes

Only minimal required fields are stored in MongoDB.

Event differentiation is handled inside the webhook route.

Merge detection is implemented using pull_request.merged flag.

Timestamp parsing supports multiple ISO formats.

The frontend is kept simple and minimal as required.

The UI polls every 15 seconds as specified in the assignment.

Author

Krishna Singh