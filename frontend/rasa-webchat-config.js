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
        socketUrl: "http://localhost:8000",
        socketPath: "/webhooks/rest/webhook",
        title: "Chatbot",
        subtitle: "Powered by Rasa",
        inputTextFieldHint: "Type a message...",
        connectingText: "Waiting for server...",
        hideWhenNotConnected: false,
        fullScreenMode: false,
        profileAvatar: "https://static.vecteezy.com/system/resources/previews/022/739/948/non_2x/chatbot-robo-advisor-chat-bot-robot-like-assistant-concept-of-digital-advisor-avatar-to-help-the-customer-icon-vector.jpg",
        openLauncherImage: "https://th.bing.com/th/id/OIP.U3EEXqgi0mbO09tcPAIV8QHaBn?rs=1&pid=ImgDetMain",
        closeLauncherImage: "https://th.bing.com/th/id/OIP.sDj44UVHnDvHHmVrNjBncwHaEo?rs=1&pid=ImgDetMain",
        params: {
            storage: "local"
        },
        customMessageDelay: (message) => {
            if (message.custom && message.custom.type === "form") {
                return 0; // No delay for form messages
            }
            return 300; // Default delay for other messages
        },
        onSocketEvent: {
            'bot_uttered': (message) => {
                if (message.custom && message.custom.type === "form") {
                    // Handle form messages
                    const form = document.createElement('form');
                    form.innerHTML = `
                        <label for="problem">Problem:</label>
                        <input type="text" id="problem" name="problem"><br>
                        <label for="location">Location:</label>
                        <input type="text" id="location" name="location"><br>
                        <label for="date">Date (YYYY-MM-DD):</label>
                        <input type="text" id="date" name="date"><br>
                        <label for="time">Time (HH:MM):</label>
                        <input type="text" id="time" name="time"><br>
                        <button type="submit">Submit</button>
                    `;
                    form.addEventListener('submit', (event) => {
                        event.preventDefault();
                        const problem = form.querySelector('#problem').value;
                        const location = form.querySelector('#location').value;
                        const date = form.querySelector('#date').value;
                        const time = form.querySelector('#time').value;
                        WebChat.send({
                            message: `/inform{"problem": "${problem}", "location": "${location}", "date": "${date}", "time": "${time}"}`,
                            custom: { type: "form" }
                        });
                    });
                    document.querySelector('#rasa-webchat').appendChild(form);
                }
            }
        },
        embedded: false, // Set to false to float the widget
        showFullScreenButton: true, // Optional: Show full screen button
        displayUnreadCount: true, // Optional: Display unread message count
        tooltipPayload: "/get_started", // Optional: Payload to send when tooltip is clicked
        tooltipText: "Need help?", // Optional: Tooltip text
        params: {
            storage: "local",
            enableScrollToBottom: true // Enable automatic scrolling
        }
    });
});