import os

import fade
import requests


class ElevenLabsTTS:

    def __init__(self, text, file_name):
        self.text = text
        self.file_name = file_name

    def generate(self):
        url = "https://api.elevenlabs.io/v1/text-to-speech/" + os.getenv("ELEVEN_LABS_VOICE_ID")
        api_key = os.getenv("ELEVEN_LABS_API_KEY")

        headers = {
            "xi-api-key": api_key
        }

        data = {
            "text": self.text,
            "voice_settings": {
                "stability": 0.25,
                "similarity_boost": 0.75
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

