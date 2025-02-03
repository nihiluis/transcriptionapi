# Transcription API
A FastAPI-based service that transcribes M4A audio files using Whisper.cpp. 

## Features
- 🎤 Audio file transcription using Whisper
- 🎵 Support for M4A audio files
- ⚡ Asynchronous processing with queue system
- 📁 Sqlite storage

## Requirements
- Python 3.12+
- FFmpeg
- Linux (perhaps MacOS is supported too)

## Getting started
```bash
# Install dependencies and setup venv
uv sync
# Run the app locally
uv run run_dev.py
# Run tests
uv run pytest
```

```bash
# Run the app in Docker
docker build -t transcriptionapi .
docker run -p 8000:8000 transcriptionapi
```
