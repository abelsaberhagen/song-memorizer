import os
import requests


class VoiceToTextElevenLabs:

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ElevenLabs API key not found. Set ELEVENLABS_API_KEY environment variable.")

    def transcribe_file(self, file_path):
        url = "https://api.elevenlabs.io/v1/speech-to-text"
        headers = {"xi-api-key": self.api_key}

        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "audio/webm")}
            response = requests.post(url, headers=headers, files=files)

        if response.status_code != 200:
            print(f"ElevenLabs STT error {response.status_code}: {response.text}")
            return None

        data = response.json()
        return data.get("text")
