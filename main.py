import os
import random
import webbrowser

import dotenv
import pyperclip
import requests
from bs4 import BeautifulSoup

dotenv.load_dotenv()

url = 'https://merkur.de'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

news_headlines = soup.find_all('a', {'class': 'id-LinkOverlay-link'})

random_headline = random.choice(news_headlines)

article_url = random_headline.get('href')

if not article_url.startswith('https:'):
    article_url = 'https:' + article_url

article_title = random_headline.get_text()
article_short = article_title.replace(' ', '-').lower()
article_response = requests.get(article_url)
article_soup = BeautifulSoup(article_response.text, 'html.parser')
article_content = article_soup.find('article', {'class': 'id-Page-mainContent'})

lead_paragraph = article_content.find('p', {'class': 'id-StoryElement-leadText'})
paragraphs = article_content.find_all('p', {'class': 'id-StoryElement-paragraph'})

full_text = article_title + ' ' + lead_paragraph.get_text() + ' ' + ' '.join(
    [paragraph.get_text() for paragraph in paragraphs])
full_text = full_text + '\n-----\n\nGenerate a catchy 30 second video script summary from this article in english without formatting, preferably in a code block'

print(full_text)

#           Uncomment to use OpenAI API when ChatGPT API is ready
#
# openai.organization = os.getenv("OPENAI_ORGANIZATION")
# openai.api_key = os.getenv("OPENAI_API_KEY")
# ai_result = openai.Completion.create(
#     model='ext-davinci-002-render-sha',
#     prompt=full_text,
#     temperature=0.7,
#     max_tokens=1000,
#     top_p=1.0,
#     frequency_penalty=0.0,
#     presence_penalty=1
# )
# print(ai_result)

pyperclip.copy(full_text)
webbrowser.open('https://chat.openai.com')

print('Copied prompt to clipboard. Open https://chat.openai.com to generate a summary.')
summary = input('Enter summary: ')

print('Generating audio file...')

url = "https://api.elevenlabs.io/v1/text-to-speech/" + os.getenv("ELEVEN_LABS_VOICE_ID")
api_key = os.getenv("ELEVEN_LABS_API_KEY")

headers = {
    "xi-api-key": api_key
}

data = {
    "text": summary
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    with open(".temp/" + article_short + ".mp3", "wb") as f:
        f.write(response.content)
    print("File saved as .temp/" + article_short + ".mp3")
else:
    print("Error:", response.status_code, response.text)
