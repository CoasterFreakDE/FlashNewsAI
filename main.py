import json
import os
import random
import shutil
from uuid import uuid4

import dotenv
import fade

from steps.ElevenLabsTTS import ElevenLabsTTS
from steps.OpenAIRequest import OpenAIRequest
from steps.TranscriptionAI import TranscriptionAI
from steps.VideoCreation import VideoCreation
from steps.YoutubeUploader import YoutubeUploader

dotenv.load_dotenv()

answers = list(os.getenv("OPTIONS"))

if __name__ == '__main__':
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
    listen = ''
    if len(answers) < 1:
        print(fade.greenblue('Do you want to start now? (y/N)'))
        listen = input()
    else:
        listen = answers[0]
    if listen != 'y':
        print(fade.greenblue('Exiting...'))
        exit(0)

    print(fade.greenblue('Generating video script...'))
    ai_output = OpenAIRequest(os.getenv("OPENAI_MODEL"), f"""
I want you to act as a storyteller. 
Over the past centuries, there were many unexplained buildings and phenomena in our universe.

I want to create a video about these unexplainable phenomena.
Write a script for a 30-second video script (only what I need to speak) about unexplainable phenomena of our universe.
Please also include information, that are not proven and just possible explanations.

{"Pick one random phenomena." if len(os.getenv('STORY_OVERRIDE')) < 1 else os.getenv('STORY_OVERRIDE')}

Just write the script. No introducing sentence. Start directly with the text, I need to say.
Start with: “Welcome to our exploration of the unexplained phenomena of our universe”.
    """).generate()

    yt_information = OpenAIRequest(os.getenv("OPENAI_MODEL"),
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
    export = ''
    if len(answers) < 2:
        print(fade.greenblue('Do you want to export the files (e) or automatically generate the video (A)?'))
        export = input()
    else:
        export = answers[1]
    if export == 'e':
        print(fade.greenblue('Exporting files...'))
        with open('output/output_' + uuid + '.txt', 'w', encoding='utf-8') as f:
            f.write(ai_output)

        shutil.copyfile(audio_file, 'output/output_' + uuid + '.mp3')

        print(fade.greenblue('Files exported.'))
        exit(0)

    transcript_steps, spoken_sentences = TranscriptionAI(audio_file).transcribe()
    print(fade.greenblue('Transcript generated.'))
    print(fade.greenblue('Generating video...'))
    video = VideoCreation(audio_file, transcript_steps, spoken_sentences).generate()
    print(fade.greenblue('Video generated.'))

    upload = ''
    if len(answers) < 3:
        print(fade.greenblue('Do you want to upload the video (u)?'))
        upload = input()
    else:
        upload = answers[2]
    if upload == 'u':
        print(fade.greenblue('Uploading video...'))
        yt = YoutubeUploader('output.mp4', yt_title, yt_description).upload()
        print(fade.greenblue('Video uploaded.'))
