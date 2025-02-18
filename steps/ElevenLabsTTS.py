import os

import fade
import requests


class ElevenLabsTTS:

    def __init__(self, text, file_name: str, voice_id, voice_data):
        self.text = text
        self.file_name = file_name
        self.voice_id = voice_id
        self.voice_data = voice_data

    def generate(self):
        url = "https://api.elevenlabs.io/v1/text-to-speech/" + self.voice_id
        api_key = os.getenv("ELEVEN_LABS_API_KEY")

        headers = {
            "xi-api-key": api_key
        }

        data = {
            "text": self.text,
            "voice_settings": {
                "stability": self.voice_data["stability"],
                "similarity_boost": self.voice_data["similarity_boost"],
            }
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            with open(".temp/" + self.file_name + ".mp3", "wb") as f:
                f.write(response.content)
            print(fade.greenblue("File saved as .temp/" + self.file_name + ".mp3"))
            return ".temp/" + self.file_name + ".mp3"
        else:
            print(fade.fire(f"Error: {response.status_code} {response.text}"))
            return None
