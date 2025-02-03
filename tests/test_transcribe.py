import pytest
import os
from transcribe import WhisperInstance
from unittest.mock import patch, MagicMock
import ffmpeg
import numpy as np

@pytest.fixture
def whisper_instance():
    # Mock whispercpp where it's imported in transcribe.py
    with patch('transcribe.Whisper', autospec=True) as mock_whisper_class:
        # Create a mock instance that will be returned by from_pretrained
        mock_instance = MagicMock()
        mock_instance.transcribe.return_value = "test transcription"
        
        # Configure the from_pretrained static method
        mock_whisper_class.from_pretrained.return_value = mock_instance
        
        instance = WhisperInstance("test_model")
        yield instance

def test_transcribe_success(whisper_instance, tmp_path):
    # Create a temporary audio file
    audio_path = tmp_path / "test.m4a"
    audio_path.write_bytes(b"dummy audio content")

    # Mock ffmpeg processing
    with patch('ffmpeg.input') as mock_input:
        mock_output = MagicMock()
        mock_input.return_value.output.return_value = mock_output
        mock_output.run.return_value = (b'\x00\x00' * 1000, None)  # Simulate audio data

        result = whisper_instance.transcribe(str(audio_path))
        
        assert result == "test transcription"
        mock_input.assert_called_once_with(str(audio_path), threads=0)

def test_transcribe_file_not_found(whisper_instance):
    with pytest.raises(FileNotFoundError) as exc_info:
        whisper_instance.transcribe("nonexistent.m4a")
    assert "Audio file not found" in str(exc_info.value)

def test_transcribe_ffmpeg_error(whisper_instance, tmp_path):
    # Create a temporary audio file
    audio_path = tmp_path / "test.m4a"
    audio_path.write_bytes(b"dummy audio content")

    # Mock ffmpeg to raise an error
    with patch('ffmpeg.input') as mock_input:
        mock_output = MagicMock()
        mock_input.return_value.output.return_value = mock_output
        mock_output.run.side_effect = ffmpeg.Error('dummy', stdout=b'', stderr=b'ffmpeg error')

        with pytest.raises(RuntimeError) as exc_info:
            whisper_instance.transcribe(str(audio_path))
        assert "Failed to load audio" in str(exc_info.value)

def test_check_ffmpeg_installed_success(whisper_instance):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock()
        # This should not raise any exception
        whisper_instance._check_ffmpeg_installed()
        mock_run.assert_called_once_with(['ffmpeg', '-version'], capture_output=True, check=True)

def test_check_ffmpeg_installed_failure(whisper_instance):
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(RuntimeError) as exc_info:
            whisper_instance._check_ffmpeg_installed()
        assert "ffmpeg is not installed" in str(exc_info.value)

def test_transcribe_removes_blank_audio(whisper_instance, tmp_path):
    # Create a temporary audio file
    audio_path = tmp_path / "test.m4a"
    audio_path.write_bytes(b"dummy audio content")

    # Mock ffmpeg processing
    with patch('ffmpeg.input') as mock_input:
        mock_output = MagicMock()
        mock_input.return_value.output.return_value = mock_output
        mock_output.run.return_value = (b'\x00\x00' * 1000, None)

        # Mock Whisper to return text with [BLANK_AUDIO]
        whisper_instance.w.transcribe.return_value = "Hello [BLANK_AUDIO] World [BLANK_AUDIO]"

        result = whisper_instance.transcribe(str(audio_path))
        
        assert result == "Hello  World"
        assert "[BLANK_AUDIO]" not in result 