from flask import Flask, request, jsonify
from rasa.core.agent import Agent
from rasa.core.interpreter import RasaNLUInterpreter
from rasa.core.channels import UserMessage, CollectingOutputChannel

app = Flask(__name__)

# Load your trained Rasa model
interpreter = RasaNLUInterpreter('./models/nlu')
agent = Agent.load('./models/core', interpreter=interpreter)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)