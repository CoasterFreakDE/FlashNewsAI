import dotenv

from steps.ElevenLabsTTS import ElevenLabsTTS
from steps.OpenAISummary import OpenAISummary
from steps.WebScraper import WebScraper

dotenv.load_dotenv()
url = 'https://merkur.de'

if __name__ == '__main__':
    full_text, article_short = WebScraper(url).scrape()
    summary = OpenAISummary('text-davinci-003', full_text).generate()
    ElevenLabsTTS(summary, article_short).generate()
