
let recorder;
let websocket;

document.getElementById('start-btn').addEventListener('click', () => {
    startRecording();
});

document.getElementById('stop-btn').addEventListener('click', () => {
    stopRecording();
});

async function startRecording() {
    console.log("Starting recording...");
    websocket = new WebSocket('ws://localhost:8000/ws');
    websocket.onopen = function() {
        console.log("WebSocket connection opened");
    };
    websocket.onmessage = function(event) {
        console.log("Received transcription: ", event.data);
        document.getElementById('transcription').innerText += event.data + '\n';
    };
    websocket.onerror = function(error) {
        console.error("WebSocket error: ", error);
    };
    websocket.onclose = function() {
        console.log("WebSocket connection closed");
    };

    let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = RecordRTC(stream, {
        type: 'audio',
        mimeType: 'audio/pcm', // Ensure PCM encoding
        recorderType: RecordRTC.StereoAudioRecorder,
        desiredSampRate: 16000,
        numberOfAudioChannels: 1,
        timeSlice: 100,  // Chunk size in milliseconds (100ms for 16000 Hz)
        ondataavailable: function(blob) {
            console.log("Sending audio data of size: ", blob.size, " bytes");
            blob.arrayBuffer().then(buffer => {
                if (websocket.readyState === WebSocket.OPEN) {
                    websocket.send(buffer);
                }
            });
        }
    });

    recorder.startRecording();
}

function stopRecording() {
    console.log("Stopping recording...");
    recorder.stopRecording(() => {
        let blob = recorder.getBlob();
        recorder.destroy();
        recorder = null;
    });

    if (websocket.readyState === WebSocket.OPEN) {
        websocket.close();
    }
}
