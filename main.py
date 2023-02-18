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
Over the past centuries, there were many unexplained buildings and phenomena in our universe. Examples are the pyramids of Giza or the hanging gardens of Babylon.

I want to create a video about these unexplainable phenomena.
Write a script for a 30-second video script (only what I need to speak) to one random, unexplainable phenomena of our universe.
Please also include information, that are not proven and just possible explanations.

Just write the script. No introducing sentence. Start directly with the text, I need to say.
Start with: “Welcome to our exploration of the unexplained phenomena of our universe”.

In addition, write a catching video title in brackets like [Title] in front of the text.
    """).generate()

    bracket_regex = re.compile(r'\[(.*?)\]')
    title = bracket_regex.findall(ai_output)[0]
    summary = bracket_regex.sub('', ai_output).strip()

    print(fade.greenblue('Title of video: ' + title))

    print(fade.greenblue('Generating audio file...'))
    eleven_labs_vid = os.getenv("ELEVEN_LABS_VOICE_ID")
    with open('voices.json', encoding='utf-8') as f:
        voices = json.load(f)
    if eleven_labs_vid == "RANDOM":
        eleven_labs_vid = random.choice(list(voices.keys()))

    selected_voice = voices[eleven_labs_vid]
    print(fade.greenblue('Selected voice: ' + selected_voice['name']))

    uuid = str(uuid4())

    audio_file = ElevenLabsTTS(summary, uuid, eleven_labs_vid, selected_voice).generate()
    if audio_file is None:
        print(fade.fire('Error generating audio file.'))

    transcript_steps = TranscriptionAI(audio_file).transcribe()
    print(fade.greenblue('Transcript generated.'))
    print(fade.greenblue('Generating video...'))
    video = VideoCreation(audio_file, transcript_steps).generate()
    print(fade.greenblue('Video generated.'))
