from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import asyncio
from typing import Optional
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

from icp.ocr.textract_utils import aws_clients
from icp.ocr.textract_utils.aws_clients_handler import get_secrets_external
from app.routers.auth import get_current_user_ws
from app.config import AWS_REGION

from amazon_transcribe.auth import CredentialResolver, Credentials

router = APIRouter()


def credentials() -> CredentialResolver:
    fresh_secrets = get_secrets_external()
    access_key, secret_key, session_token = fresh_secrets

    # Create an instance of Credentials with the new credentials
    credentials = Credentials(
        access_key_id=access_key,
        secret_access_key=secret_key,
        session_token=session_token
    )

    class CustomCredentialResolver(CredentialResolver):
        async def get_credentials(self) -> Optional[Credentials]:
            return credentials

    return CustomCredentialResolver()

class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream, websocket):
        super().__init__(output_stream)
        self.websocket = websocket
        self.last_transcript = ""

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                new_transcript = alt.transcript
                new_part = new_transcript.replace(self.last_transcript,"")
                if new_part:
                    self.last_transcript = new_transcript
                    await self.websocket.send_text(new_part)
                    

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for handling real-time transcription.
    This endpoint accepts a WebSocket connection,sets up a transcription stream with Amazon Transcribe.

    Args:
        websocket: The WebSocket connection instance.

    Response:
        Streams the transcribed text
    """
    user = await get_current_user_ws(websocket)
    if not user:
        return JSONResponse(status_code=403, content={"message":"Unauthorized"})
    await websocket.accept()
    credential_resolver = credentials()
    client = TranscribeStreamingClient(region=AWS_REGION,credential_resolver = credential_resolver)
    #client = aws_clients.get('transcribe')
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
        enable_partial_results_stabilization = True,
        partial_results_stability="low",
    )
    handler = MyEventHandler(stream.output_stream, websocket)
    try:
        await asyncio.gather(handler.handle_events(), receive_audio(websocket, stream))
    except WebSocketDisconnect:
        await stream.input_stream.end_stream()
    finally:
        print("WebSocket closed")

async def receive_audio(websocket: WebSocket, stream):
    while True:
        data = await websocket.receive_bytes()
        if data:
            await stream.input_stream.send_audio_event(audio_chunk=data)
        else:
            await stream.input_stream.send_audio_event(audio_chunk=b'\x00' * 320)  # 16000 Hz * 0.02s * 2 bytes/sample = 320 bytes of silence
