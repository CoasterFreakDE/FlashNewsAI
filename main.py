import json
import os
import random
import sys

import dotenv
import fade

from steps.ElevenLabsTTS import ElevenLabsTTS
from steps.OpenAISummary import OpenAISummary
from steps.TranscriptionAI import TranscriptionAI
from steps.WebScraper import WebScraper

dotenv.load_dotenv()
url = 'https://merkur.de/welt'

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
⣿⡟⠄⠄⣾⣇⠷⣢⣿⣿⣿⣿⣿⣿⣿⣭⣀⡈⠙⢿⣿⣿⡇⡧⢁⣾⣿⣿⣿⣿⣿⢏⣾      Welcome to FlashNewsAI
⣿⡇⠄⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢻⠇⠄⠄⢿⣿⡇⢡⣾⣿⣿⣿⣿⣿⣏⣼⣿      A project by @CoasterFreakDE
⣿⣷⢰⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⢰⣧⣀⡄⢀⠘⡿⣰⣿⣿⣿⣿⣿⣿⠟⣼⣿⣿
⢹⣿⢸⣿⣿⠟⠻⢿⣿⣿⣿⣿⣿⣿⣿⣶⣭⣉⣤⣿⢈⣼⣿⣿⣿⣿⣿⣿⠏⣾⣹⣿⣿    This project is licensed under the GPL3 License.
⢸⠇⡜⣿⡟⠄⠄⠄⠈⠙⣿⣿⣿⣿⣿⣿⣿⣿⠟⣱⣻⣿⣿⣿⣿⣿⠟⠁⢳⠃⣿⣿⣿
⠄⣰⡗⠹⣿⣄⠄⠄⠄⢀⣿⣿⣿⣿⣿⣿⠟⣅⣥⣿⣿⣿⣿⠿⠋⠄⠄⣾⡌⢠⣿⡿⠃
⠜⠋⢠⣷⢻⣿⣿⣶⣾⣿⣿⣿⣿⠿⣛⣥⣾⣿⠿⠟⠛⠉⠄⠄
            """)
        )
        print(fade.greenblue('Please enter the URL of the article you want to listen to: (https://merkur.de/welt)'))
        url = input() or url
        print(fade.greenblue(f'Do you want to scrape the article from {url} now? (y/N)'))
        listen = input()
        if listen != 'y':
            print(fade.greenblue('Exiting...'))
            exit(0)

    print(fade.greenblue('Scraping article...'))
    full_text, full_text_without_prompt, article_title, article_short = WebScraper(url).scrape()
    print(fade.greenblue('Generating summary...'))
    summary = OpenAISummary('text-davinci-003', full_text).generate()
    print(fade.greenblue('Generating audio file...'))
    eleven_labs_vid = os.getenv("ELEVEN_LABS_VOICE_ID")
    if eleven_labs_vid == "RANDOM":
        with open('voices.json', encoding='utf-8') as f:
            voices = json.load(f)
            eleven_labs_vid = random.choice(list(voices.keys()))

    selected_voice = voices[eleven_labs_vid]

    print(fade.greenblue('Selected voice: ' + selected_voice['name']))

    audio_file = ElevenLabsTTS(summary, article_short, eleven_labs_vid, selected_voice).generate()
    if audio_file is None:
        print(fade.fire('Error generating audio file.'))

    transcript = TranscriptionAI(audio_file).transcribe()
    print(fade.greenblue('Transcript:'))
    print(transcript)
