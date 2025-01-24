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
        subtitle: "Powered by Rasa",
        onSocketEvent: {
            'bot_uttered': (message) => {
                handleBotResponse(message);
            }
        }
    });

    function initializeWebSocket() {
        const socket = new WebSocket("ws://localhost:5005/webhooks/socket");
    
        socket.onopen = function(event) {
            console.log("WebSocket connection established:", event);
        };
    
        socket.onmessage = function(event) {
            const message = JSON.parse(event.data);
            handleBotResponse(message);
        };
    
        socket.onclose = function(event) {
            console.log("WebSocket connection closed:", event);
        };
    
        socket.onerror = function(error) {
            console.error("WebSocket error:", error);
        };
    
        // Handle user input
        const userInputForm = document.getElementById('user-input-form');
        userInputForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const userInput = document.getElementById('user-input').value;
            if (userInput) {
                displayUserMessage(userInput);
                socket.send(JSON.stringify({ message: userInput }));
                document.getElementById('user-input').value = '';
            }
        });
    }
    
    function handleBotResponse(message) {
        const chatContainer = document.getElementById('chat-container');
    
        if (message.text) {
            const botMessage = document.createElement('div');
            botMessage.innerHTML = `
                <div style="background-color: #e0f7fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>Bot:</strong> ${message.text}
                </div>
            `;
            chatContainer.appendChild(botMessage);
        }
    
        if (message.custom) {
            if (message.custom.type === "clinic_list") {
                const clinicList = document.createElement('div');
                clinicList.innerHTML = `
                    <div style="background-color: #e0f7fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <strong>Available Clinics:</strong>
                        <ul>
                            ${message.custom.clinics.map(clinic => `<li>${clinic.name} - ${clinic.address}</li>`).join('')}
                        </ul>
                    </div>
                `;
                chatContainer.appendChild(clinicList);
            }
    
            if (message.custom.type === "appointment_confirmation") {
                const appointmentDetails = message.custom.appointment_details;
                const confirmationMessage = document.createElement('div');
                confirmationMessage.innerHTML = `
                    <div style="background-color: #e0f7fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <strong>Appointment Confirmation:</strong>
                        <p>Your appointment with Dr. ${appointmentDetails.doctor} on ${appointmentDetails.date} at ${appointmentDetails.time} has been confirmed.</p>
                    </div>
                `;
                chatContainer.appendChild(confirmationMessage);
            }
        }
    
        // Scroll to the bottom of the chat container
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    function displayUserMessage(message) {
        const chatContainer = document.getElementById('chat-container');
        const userMessage = document.createElement('div');
        userMessage.innerHTML = `
            <div style="background-color: #d1c4e9; padding: 10px; border-radius: 5px; margin-bottom: 10px; text-align: right;">
                <strong>You:</strong> ${message}
            </div>
        `;
        chatContainer.appendChild(userMessage);
    
        // Scroll to the bottom of the chat container
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Initialize the WebSocket connection
    initializeWebSocket();
});