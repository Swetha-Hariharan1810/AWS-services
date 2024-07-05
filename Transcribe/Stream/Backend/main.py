
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import logging
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream, websocket):
        super().__init__(output_stream)
        self.websocket = websocket

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                logger.info(f"Transcription: {alt.transcript}")
                await self.websocket.send_text(alt.transcript)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    client = TranscribeStreamingClient(region="us-west-2")
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
    )
    handler = MyEventHandler(stream.output_stream, websocket)
    try:
        await asyncio.gather(handler.handle_events(), receive_audio(websocket, stream))
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        await stream.input_stream.end_stream()
    finally:
        logger.info("WebSocket closed")

async def receive_audio(websocket: WebSocket, stream):
    while True:
        data = await websocket.receive_bytes()
        if data:
            logger.info(f"Received audio data of size: {len(data)} bytes")
            await stream.input_stream.send_audio_event(audio_chunk=data)
        else:
            logger.info("Received empty data, sending silence")
            await stream.input_stream.send_audio_event(audio_chunk=b'\x00' * 320)  # 16000 Hz * 0.02s * 2 bytes/sample = 320 bytes of silence
