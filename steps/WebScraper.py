import random

import requests
from bs4 import BeautifulSoup


class WebScraper:

    def __init__(self, url):
        self.url = url

    def scrape(self):
        response = requests.get(self.url)

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
        full_text = full_text + '\n-----\n\nGenerate a catchy 30 second video script summary from this article in ' \
                                'english without formatting. Only return the text that should be spoken.'
        return full_text, article_short
