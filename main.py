import os
import random
import time

import dotenv
import openai
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
full_text = full_text + '\n-----\n\nGenerate a catchy 30 second video script summary from this article in english ' \
                        'without formatting. Only return the text that should be spoken.'

print(full_text)

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")

start_time = time.time()

response = openai.Completion.create(
    model='text-davinci-003',
    prompt=full_text,
    temperature=1,
    max_tokens=1000,
    stream=True,
)

# create variables to collect the stream of events
collected_events = []
completion_text = ''
# iterate through the stream of events
for event in response:
    event_time = time.time() - start_time  # calculate the time delay of the event
    collected_events.append(event)  # save the event response
    event_text = event['choices'][0]['text']  # extract the text
    completion_text += event_text  # append the text
    print(f"Text received: {event_text} ({event_time:.2f} seconds after request)")  # print the delay and text

# print the time delay and text received
print(f"Full response received {event_time:.2f} seconds after request")
print(f"Full text received: {completion_text}")

summary = completion_text
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
