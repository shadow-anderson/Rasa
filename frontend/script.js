document.addEventListener("DOMContentLoaded", function() {
    // Display a welcome message
    const chatContainer = document.getElementById('chat-container');
    const welcomeMessage = document.createElement('div');
    welcomeMessage.innerHTML = `
        <div style="background-color: #e0f7fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <strong>Welcome!</strong> How can I assist you today?
        </div>
    `;
    chatContainer.insertBefore(welcomeMessage, chatContainer.firstChild);

    // Initialize Rasa Webchat widget
    WebChat.default.init({
        selector: "#rasa-webchat",
        initPayload: "/get_started",
        customData: {"language": "en"}, // arbitrary custom data
        socketUrl: "http://localhost:5005",
        title: "Chatbot",
        subtitle: "Powered by Rasa"
    });
});