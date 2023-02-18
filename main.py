import json
import os
import random
import re
import sys
from uuid import uuid4

import dotenv
import fade

from steps.ElevenLabsTTS import ElevenLabsTTS
from steps.OpenAIRequest import OpenAIRequest
from steps.TranscriptionAI import TranscriptionAI
from steps.VideoCreation import VideoCreation
from steps.YoutubeUploader import YoutubeUploader

dotenv.load_dotenv()

if __name__ == '__main__':
    system_args = sys.argv
    direct = False
    if len(system_args) > 1:
        direct = system_args[1] == '-f'

    if not direct:
        print(
            fade.greenblue("""
⣱⣿⣿⡟⡐⣰⣧⡷⣿⣴⣧⣤⣼⣯⢸⡿⠁⣰⠟⢀⣼⠏⣲⠏⢸⣿⡟⣿⣿⣿⣿⣿⣿
⣿⣿⡟⠁⠄⠟⣁⠄⢡⣿⣿⣿⣿⣿⣿⣦⣼⢟⢀⡼⠃⡹⠃⡀⢸⡿⢸⣿⣿⣿⣿⣿⡟
⣿⣿⠃⠄⢀⣾⠋⠓⢰⣿⣿⣿⣿⣿⣿⠿⣿⣿⣾⣅⢔⣕⡇⡇⡼⢁⣿⣿⣿⣿⣿⣿⢣
⣿⡟⠄⠄⣾⣇⠷⣢⣿⣿⣿⣿⣿⣿⣿⣭⣀⡈⠙⢿⣿⣿⡇⡧⢁⣾⣿⣿⣿⣿⣿⢏⣾      Welcome to unexplained phenomena of our universe!
⣿⡇⠄⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢻⠇⠄⠄⢿⣿⡇⢡⣾⣿⣿⣿⣿⣿⣏⣼⣿      A project by @CoasterFreakDE
⣿⣷⢰⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⢰⣧⣀⡄⢀⠘⡿⣰⣿⣿⣿⣿⣿⣿⠟⣼⣿⣿
⢹⣿⢸⣿⣿⠟⠻⢿⣿⣿⣿⣿⣿⣿⣿⣶⣭⣉⣤⣿⢈⣼⣿⣿⣿⣿⣿⣿⠏⣾⣹⣿⣿    This project is licensed under the GPL3 License.
⢸⠇⡜⣿⡟⠄⠄⠄⠈⠙⣿⣿⣿⣿⣿⣿⣿⣿⠟⣱⣻⣿⣿⣿⣿⣿⠟⠁⢳⠃⣿⣿⣿
⠄⣰⡗⠹⣿⣄⠄⠄⠄⢀⣿⣿⣿⣿⣿⣿⠟⣅⣥⣿⣿⣿⣿⠿⠋⠄⠄⣾⡌⢠⣿⡿⠃
⠜⠋⢠⣷⢻⣿⣿⣶⣾⣿⣿⣿⣿⠿⣛⣥⣾⣿⠿⠟⠛⠉⠄⠄
            """)
        )
        print(fade.greenblue(f'Do you want to start now? (y/N)'))
        listen = input()
        if listen != 'y':
            print(fade.greenblue('Exiting...'))
            exit(0)

    print(fade.greenblue('Generating video script...'))
    ai_output = OpenAIRequest('text-davinci-003', """
I want you to act as a storyteller. 
Over the past centuries, there were many unexplained buildings and phenomena in our universe.

I want to create a video about these unexplainable phenomena.
Write a script for a 30-second video script (only what I need to speak) to one random, unexplainable phenomena of our universe.
Please also include information, that are not proven and just possible explanations.

Just write the script. No introducing sentence. Start directly with the text, I need to say.
Start with: “Welcome to our exploration of the unexplained phenomena of our universe”.
    """).generate()

    yt_information = OpenAIRequest('text-davinci-003',
                                   "Generate a catching youtube title and description (seperated by @) without"
                                   " formatting for the following video script: " + ai_output).generate()

    yt_title = yt_information.split('@')[0]
    yt_description = yt_information.split('@')[1]

    print(fade.greenblue('Title: ' + yt_title))
    print(fade.greenblue('Description: ' + yt_description))

    print(fade.greenblue('Generating audio file...'))
    eleven_labs_vid = os.getenv("ELEVEN_LABS_VOICE_ID")
    with open('voices.json', encoding='utf-8') as f:
        voices = json.load(f)
    if eleven_labs_vid == "RANDOM":
        eleven_labs_vid = random.choice(list(voices.keys()))

    selected_voice = voices[eleven_labs_vid]
    print(fade.greenblue('Selected voice: ' + selected_voice['name']))

    uuid = str(uuid4())

    audio_file = ElevenLabsTTS(ai_output, uuid, eleven_labs_vid, selected_voice).generate()
    if audio_file is None:
        print(fade.fire('Error generating audio file.'))

    transcript_steps, spoken_sentences = TranscriptionAI(audio_file).transcribe()
    print(fade.greenblue('Transcript generated.'))
    print(fade.greenblue('Generating video...'))
    video = VideoCreation(audio_file, transcript_steps, spoken_sentences).generate()
    print(fade.greenblue('Video generated.'))
    print(fade.greenblue('Uploading video...'))
    yt = YoutubeUploader('output.mp4', yt_title, yt_description).upload()
    print(fade.greenblue('Video uploaded.'))
