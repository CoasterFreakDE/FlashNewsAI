import json
import os
import time
import urllib.parse

import fade
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

        url_encoded_pipeline = urllib.parse.quote(json.dumps(pipeline))

        response = requests.post('https://api.oneai.com/api/v0/pipeline/async/file?pipeline=' + url_encoded_pipeline,
                                 headers=headers, files=files)
        output = response.json()

        print(output)

        if output['status'] == 'QUEUED':
            task_id = output['task_id']

            while True:
                task_response = requests.get('https://api.oneai.com/api/v0/pipeline/async/tasks/' + task_id, headers=headers).json()

                print(task_response)

                if task_response['status'] == 'COMPLETED':
                    spoken_text = task_response['result']['output'][0]['text']

                    # Split the spoken_text by newlines
                    lines = spoken_text.split('\n')

                    # Filter the lines that contain spoken sentences
                    spoken_sentences = [line[line.index(':') + 1:] for line in lines if ':' in line]

                    return task_response['result']['output'][0]['labels'], spoken_sentences

                if task_response['status'] == 'FAILED':
                    status_code = task_response['result']['status_code']
                    message = task_response['result']['message']

                    # throw error
                    raise Exception(f"[status_code {status_code}] {message}")

                print(fade.greenblue(f'Waiting for transcription to complete...'))
                time.sleep(5)

        spoken_text = output['result']['output'][0]['text']

        # Split the spoken_text by newlines
        lines = spoken_text.split('\n')

        # Filter the lines that contain spoken sentences
        spoken_sentences = [line[line.index(':') + 1:] for line in lines if ':' in line]
        return output['result']['output'][0]['labels'], spoken_sentences

