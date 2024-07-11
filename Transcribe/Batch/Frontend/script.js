let isRecording = false;
let mediaRecorder;
let chunks = [];
const chatSpace = document.getElementById('chatSpace');

// Function to start or stop recording
async function toggleRecording() {
    if (!isRecording) {
        // Start recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = (event) => {
                chunks.push(event.data);
            };
            mediaRecorder.onstop = async () => {
                const blob = new Blob(chunks, { type: 'audio/wav' });
                chunks = [];
                const file_id = generateUUID();
                const filename = file_id + ".wav";
                displayMessage("file created: " + filename);
                console.log(filename);
                const formData = new FormData();
                formData.append('file', blob, filename);
                formData.append('file_id', file_id);

                try {
                    const response = await fetch('http://localhost:8000/upload', {
                        method: 'POST',
                        body: formData,
                    });

                    if (response.ok) {
                        const data = await response.json();
                        console.log(data.message); // Log the message from the backend
                        displayMessage(data.message); // Display message in chat space
                    } else {
                        console.error('Failed to upload audio file.');
                        displayMessage('Failed to upload audio file.');
                    }
                } catch (error) {
                    console.error('Error uploading audio file:', error);
                    displayMessage('Error uploading audio file.');
                }
            };

            mediaRecorder.start();
            console.log('Recording started.');
            document.getElementById('recordButton').textContent = 'Stop Recording';
            isRecording = true;
        } catch (error) {
            console.error('Error starting recording:', error);
            displayMessage('Error starting recording.');
        }
    } else {
        // Stop recording
        mediaRecorder.stop();
        console.log('Recording stopped.');
        document.getElementById('recordButton').textContent = 'Record';
        isRecording = false;
    }
}

// Function to display message in chat space
function displayMessage(message) {
    const messageElement = document.createElement('p');
    messageElement.textContent = message;
    chatSpace.appendChild(messageElement);
    chatSpace.scrollTop = chatSpace.scrollHeight; // Auto-scroll to bottom
}

// Event listener for record button click
document.getElementById('recordButton').addEventListener('click', () => {
    toggleRecording();
});

// Function to generate UUID (v4)
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0,
              v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}
