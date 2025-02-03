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
uv sync
uv run run_dev.py
```