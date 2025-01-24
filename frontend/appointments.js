document.addEventListener("DOMContentLoaded", function() {
    const chatContainer = document.getElementById('chat-container');

    function displayClinicRecommendations(clinics) {
        const clinicList = document.createElement('div');
        clinicList.innerHTML = `
            <div style="background-color: #e0f7fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <strong>Top Clinic Recommendations:</strong>
                <ul>
                    ${clinics.map(clinic => `<li>${clinic.name} located at ${clinic.location}, Rating: ${clinic.rating}</li>`).join('')}
                </ul>
            </div>
        `;
        chatContainer.appendChild(clinicList);
    }

    function collectAndValidateInputs() {
        const problem = document.getElementById('problem').value;
        const location = document.getElementById('location').value;
        const date = document.getElementById('date').value;
        const time = document.getElementById('time').value;

        if (!problem || !location || !date || !time) {
            alert("Please fill in all the fields.");
            return null;
        }

        const datePattern = /^\d{4}-\d{2}-\d{2}$/;
        const timePattern = /^([01]\d|2[0-3]):([0-5]\d)$/;

        if (!datePattern.test(date)) {
            alert("Please enter the date in YYYY-MM-DD format.");
            return null;
        }

        if (!timePattern.test(time)) {
            alert("Please enter the time in HH:MM format.");
            return null;
        }

        return { problem, location, date, time };
    }

    function sendAppointmentData(data) {
        fetch('http://localhost:5005/webhooks/rest/webhook', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sender: 'user',
                message: `/inform{"problem": "${data.problem}", "location": "${data.location}", "date": "${data.date}", "time": "${data.time}"}`
            })
        })
        .then(response => response.json())
        .then(messages => {
            messages.forEach(message => {
                handleBotResponse(message);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function handleBotResponse(message) {
        if (message.text) {
            const responseMessage = document.createElement('div');
            responseMessage.innerHTML = `
                <div style="background-color: #f1f1f1; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    ${message.text}
                </div>
            `;
            chatContainer.appendChild(responseMessage);
        }

        if (message.custom && message.custom.type === "clinic_recommendations") {
            displayClinicRecommendations(message.custom.clinics);
        }

        if (message.custom && message.custom.type === "appointment_confirmation") {
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

    // Example usage
    document.getElementById('submit-button').addEventListener('click', function() {
        const data = collectAndValidateInputs();
        if (data) {
            sendAppointmentData(data);
        }
    });
});