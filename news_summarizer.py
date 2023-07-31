import os
import json
import requests
import nltk
from newsapi import NewsApiClient
from newsplease import NewsPlease
from dotenv import load_dotenv

load_dotenv()
nltk.download('punkt')


class NewsSummarizer:
    def __init__(self):
        self.newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
        self.headers = {"Authorization": f"Bearer {os.getenv('AI_API_KEY')}"}
        self.categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
        self.categories_dict = {category: [] for category in self.categories}
        self.article_count = 3

    def get_top_headlines_for_categories(self):
        for category in self.categories:
            count = 0
            top_headlines = self.newsapi.get_top_headlines(country='us', category=category)
            while len(self.categories_dict[category]) != self.article_count and count < len(top_headlines['articles']):
                try:
                    article = NewsPlease.from_url(top_headlines['articles'][count]['url'])
                    if article.maintext and \
                            'This copy is for your personal, non-commercial use only.' not in article.maintext:
                        self.categories_dict[category].append(article.maintext)
                except Exception as e:
                    print(f"Error occurred while processing article: {e}")

                count += 1

    def summarize_categories(self):
        for category in self.categories:
            main_text_combined = tokenize_and_cut('.'.join(self.categories_dict[category]))
            payload = {
                "providers": "openai",
                "language": 'en',
                "text": 'summarize all the information in a paragraph, give me a rundown '
                        'of this information:' + main_text_combined}
            response = requests.post("https://api.edenai.run/v2/text/summarize", json=payload, headers=self.headers)
            print(response.text)
            self.categories_dict[category] = json.loads(response.text)['openai']['result']

    def get_summarized_news(self):
        self.get_top_headlines_for_categories()
        self.summarize_categories()
        return self.categories_dict


def tokenize_and_cut(text, max_tokens=3000):
    tokens = nltk.word_tokenize(text)
    return ' '.join(tokens[:max_tokens])
