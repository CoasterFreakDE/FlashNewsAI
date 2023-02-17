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
        print(fade.greenblue(f'Do you want to scrape the article from {url} now? (y/n)'))
        listen = input()
        if listen != 'y':
            print(fade.greenblue('Exiting...'))
            exit(0)

    print(fade.greenblue('Scraping article...'))
    full_text, full_text_without_prompt, article_title, article_short = WebScraper(url).scrape()
    print(fade.greenblue('Generating summary...'))
    summary = OpenAISummary('text-davinci-003', full_text).generate()
    print(fade.greenblue('Generating audio file...'))
    audio_file = ElevenLabsTTS(summary, article_short).generate()
    if audio_file is None:
        print(fade.fire('Error generating audio file.'))

    transcript = TranscriptionAI(audio_file).transcribe()
    print(fade.greenblue('Transcript:'))
    print(transcript)


