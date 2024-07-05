# Live Audio Transcription with FastAPI and Amazon Transcribe

## Overview

This project provides a real-time audio transcription service using FastAPI for the backend and Amazon Transcribe for live transcription. The frontend captures audio using RecordRTC, sends it to the backend via WebSockets, and displays the transcribed text in real-time.

## Directory Structure

```plaintext
transcribe_project/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── amazon_transcribe_client.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── styles.css
