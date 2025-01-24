from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import warnings
from rasa.core.agent import Agent
from rasa.nlu.model import Interpreter as RasaNLUInterpreter
from rasa.core.channels import UserMessage, CollectingOutputChannel
import os

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app)  # Enable CORS for frontend-backend communication

warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"

# Load your trained Rasa model
interpreter = RasaNLUInterpreter('./models/nlu')
agent = Agent.load('./models/core', interpreter=interpreter)

# Serve static files (frontend)
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

# Webhook to handle Rasa messages
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    user_message = data.get('message')
    sender_id = data.get('sender_id', 'default')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Process the message with Rasa
    output_channel = CollectingOutputChannel()
    agent.handle_message(UserMessage(user_message, output_channel, sender_id))

    responses = [message['text'] for message in output_channel.messages]
    return jsonify({"responses": responses})

# API to interact with database (optional)
@app.route('/api/clinics', methods=['GET'])
def get_clinics():
    # Example query to fetch clinics (replace with your actual DB logic)
    clinics = [{"name": "Clinic A", "location": "Delhi", "slots": ["9:00 AM", "10:00 AM"]}]
    return jsonify(clinics)

if __name__ == '__main__':
    # Start Flask app
    app.run(host='0.0.0.0', port=8000)