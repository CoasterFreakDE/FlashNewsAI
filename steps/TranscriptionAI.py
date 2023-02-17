import os

import requests


class TranscriptionAI:

    def __init__(self, audio_file):
        self.audio_file = audio_file

    def transcribe(self):
        api_key = os.getenv("ONEAI_API_KEY")
        headers = {
            "accept": "application/json",
            "api-key": api_key
        }

        pipeline = {
            "input_type": "conversation",
            "content_type": "audio/mpeg",
            "steps": [
                {
                    "skill": "transcribe",
                    "params": {
                        "speaker_detection": False,
                        "timestamp_per_word": True
                    }
                }
            ]
        }

        files = {
            "file": ("file.mp3", open(self.audio_file, "rb"), "audio/mpeg")
        }

        response = requests.post('https://api.oneai.com/api/v0/pipeline/async/file?pipeline=%7B%0A%20%20%20%20'
                                 '%22input_type%22%3A%20%22conversation%22%2C%0A%20%20%20%20%22content_type%22%3A%20'
                                 '%22audio%2Fwav%22%2C%0A%20%20%20%20%22steps%22%3A%20%5B%0A%20%20%20%20%20%20%7B%0A'
                                 '%20%20%20%20%20%20%20%20%22skill%22%3A%20%22transcribe%22%0A%20%20%20%20%20%20%7D'
                                 '%0A%20%20%20%20%5D%0A%7D', headers=headers, data=pipeline, files=files)
        output = response.json()
        return output

