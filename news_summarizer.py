import os
import time
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from newsplease import NewsPlease
import google.generativeai as palm
from the_athletic_parser import TheAthleticParser

load_dotenv()

ARTICLE_COUNT = 3
RETRY_ATTEMPTS = 3
API_REQUEST_INTERVAL = 10

palm.configure(api_key=os.getenv('AI_API_KEY'))
nyt_api_key = os.getenv('NYT_API_KEY')
proxy_key = os.getenv('PROXY_API_KEY')

client = MongoClient(os.environ.get('MONGO_URI'))
news_collection = client.users["news"]

DEFAULTS = {
    'model': 'models/text-bison-001',
    'temperature': 0.6,
    'candidate_count': 1,
    'top_k': 40,
    'top_p': 0.95,
    'max_output_tokens': 1024,
    'stop_sequences': [],
    'safety_settings': [{"category": "HARM_CATEGORY_DEROGATORY", "threshold": 3},
                        {"category": "HARM_CATEGORY_TOXICITY", "threshold": 3},
                        {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 3},
                        {"category": "HARM_CATEGORY_SEXUAL", "threshold": 3},
                        {"category": "HARM_CATEGORY_MEDICAL", "threshold": 3},
                        {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 3}],
}


class NewsSummarizer:
    """
    A class for summarizing news articles from various categories.
    """

    def __init__(self):
        """
        Initialize the NewsSummarizer class with a list of categories and an empty dictionary for storing articles.
        """
        self.categories = [
            "arts", "automobiles", "business", "fashion", "food",
            "health", "home", "insider", "magazine", "movies",
            "politics", "realestate", "nyregion", "science", "sports",
            "technology", "theater", "travel", "us", "world"
        ]
        self.categories_dict = {category: [] for category in self.categories}

    def get_top_headlines_for_categories(self):
        """
        Retrieve top headlines for each category and store them in the categories_dict dictionary.
        """
        for category in self.categories:
            prev_articles = [document["title"].lower() for document in news_collection.find({"category": category})]
            if len(prev_articles) >= 6:
                news_collection.delete_many({"category": category})
            articles_data = fetch_articles_for_category(category)
            valid_articles_count = 0
            for article_data in articles_data:
                if valid_articles_count >= ARTICLE_COUNT:
                    break

                summarized_content = scrape_content(article_data.get("url"), category)
                image = article_data.get("multimedia")
                title = article_data.get("title")
                url = article_data.get("url")

                if all([summarized_content, image, title, url, title.lower() not in prev_articles]):
                    valid_articles_count += 1
                    article_info = {
                        "category": category,
                        "image": image[0].get("url"),
                        "title": title,
                        "url": url,
                        "content": summarized_content
                    }
                    news_collection.insert_one(article_info)
                    self.categories_dict[category].append(article_info)

                time.sleep(API_REQUEST_INTERVAL)

    def get_summarized_news(self):
        """
        Retrieve and summarize news articles for all categories.

        :return: A dictionary containing summarized news articles for each category.
        :rtype: dict
        """
        self.get_top_headlines_for_categories()
        return self.categories_dict


def scrape_content(article_url, category):
    """
    Extract and summarize article content from the article url.

    :param category: The genre/category of which the article is in.
    :type category: str
    :param article_url: URL of the article.
    :type article_url: str

    :return: Summarized content of the article as a string, or None if summarization fails.
    :rtype: str | None
    """
    for attempt in range(RETRY_ATTEMPTS):
        try:
            article = NewsPlease.from_url(f'http://api.proxiesapi.com/?auth_key={proxy_key}&url={article_url}')
            summarized_content = summarize_article(article.maintext, category)
            return summarized_content
        except Exception as e:
            print(f"Error scraping article in {category}: {str(e)} {attempt + 1} / {RETRY_ATTEMPTS}")
    return None


def fetch_articles_for_category(category):
    """
    Fetch top articles for a specific category from the New York Times API.

    :param category: The category for which to fetch articles.
    :type category: str

    :return: list, A list of dictionaries containing article information.
    :rtype: list
    """
    for attempt in range(RETRY_ATTEMPTS):
        try:
            if category != 'sports':
                endpoint = f'https://api.nytimes.com/svc/topstories/v2/{category}.json?api-key={nyt_api_key}'
                response = requests.get(endpoint)
                return response.json().get('results', [])
            else:
                return TheAthleticParser().get_articles()
        except Exception as e:
            print(f"Error fetching articles for {category}: {str(e)} {attempt + 1} / {RETRY_ATTEMPTS}")
    return []


def summarize_article(content, category):
    """
    Summarize the provided article content using the Google PaLM AI model.

    :param category: The category of which the article is in.
    :type category: str
    :param content: The content of the article to be summarized.
    :type content: str

    :return: str, The summarized article text.
    :rtype: str
    """
    for attempt in range(RETRY_ATTEMPTS):
        try:
            prompt = f"Summarize this news article in a comprehensive paragraph, without using bullet points:{content}"
            response = palm.generate_text(**DEFAULTS, prompt=prompt)
            return response.result if response is not None else ""
        except Exception as e:
            print(f"Error occurred while summarizing the article {category}: {str(e)} {attempt + 1} / {RETRY_ATTEMPTS}")
    return ""
