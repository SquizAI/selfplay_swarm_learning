# web_scraping.py
import requests
from bs4 import BeautifulSoup

def scrape_ai_news():
    url = "https://techcrunch.com/tag/ai/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    for article in articles[:5]:  # Get top 5 articles
        title = article.find('h2').text
        print(f"Article Title: {title}")
        # Send this information back to the game for dynamic content generation
