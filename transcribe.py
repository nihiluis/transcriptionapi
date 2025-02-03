from whispercpp import Whisper
import ffmpeg
import numpy as np
import os
import subprocess



class WhisperInstance:
    def __init__(self, model_name: str):
        self._check_ffmpeg_installed()
        self.w = Whisper.from_pretrained(model_name)

    def _check_ffmpeg_installed(self):
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise RuntimeError("ffmpeg is not installed. Please install ffmpeg to use this transcriber.")

    def transcribe(self, audio_path: str):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            y, _ = (
                ffmpeg.input(audio_path, threads=0)
                    .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=16000)
                    .run(
                        cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True
                    )
            )
        except ffmpeg.Error as e:
            raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

        arr = np.frombuffer(y, np.int16).flatten().astype(np.float32) / 32768.0
        result = self.w.transcribe(arr)
        result = result.replace("[BLANK_AUDIO]", "").strip()
        return result
