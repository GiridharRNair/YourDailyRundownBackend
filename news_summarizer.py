import os
import time
import requests
from dotenv import load_dotenv
import google.generativeai as palm
from newsplease import NewsPlease

load_dotenv()

ARTICLE_COUNT = 3
RETRY_ATTEMPTS = 3
API_REQUEST_INTERVAL = 10

palm.configure(api_key=os.getenv('AI_API_KEY'))
nyt_api_key = os.getenv('NYT_API_KEY')


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
            articles_data = fetch_articles_for_category(category)
            valid_articles_count = 0
            for article_data in articles_data:
                if valid_articles_count >= ARTICLE_COUNT:
                    break
                scraped_article = extract_article_details(article_data.get("url"), article_data.get("title"), category)
                if scraped_article:
                    valid_articles_count += 1
                    self.categories_dict[category].append(scraped_article)
                time.sleep(API_REQUEST_INTERVAL)

    def get_summarized_news(self):
        """
        Retrieve and summarize news articles for all categories.

        :return: A dictionary containing summarized news articles for each category.
        :rtype: dict
        """
        self.get_top_headlines_for_categories()
        return self.categories_dict


def extract_article_details(article_url, article_title, category):
    """
    Extract article details, summarize the content, and return a dictionary with relevant information.

    :param article_url: str, URL of the article.
    :param article_title: str, Title of the article.
    :param category: str, Category of the article.

    :return: dict, A dictionary containing title, URL, and summarized content of the article.
    :rtype: dict
    """
    try:
        article = NewsPlease.from_url(article_url)
        content = article.maintext
        summarized_content = summarize_article(content)
        if summarized_content is not None:
            return {"title": article_title, "url": article_url, "content": summarized_content}
    except Exception as e:
        print(f"Error summarizing article in {category.title()}: {str(e)}")


def fetch_articles_for_category(category):
    """
    Fetch top articles for a specific category from the New York Times API.

    :param category: str, The category for which to fetch articles.

    :return: list, A list of dictionaries containing article information.
    :rtype: list
    """
    for attempt in range(RETRY_ATTEMPTS):
        response = requests.get(f'https://api.nytimes.com/svc/topstories/v2/{category}.json?api-key={nyt_api_key}')
        if response.status_code == 200:
            return response.json().get('results', [])
        elif response.status_code == 504:
            print(f"502 Bad Gateway Error - Retry attempt {attempt + 1}/{RETRY_ATTEMPTS}")
            time.sleep(API_REQUEST_INTERVAL)
        else:
            print(f"Error fetching articles for {category}: {response.status_code}")
            return []

    print(f"Unable to fetch articles for {category} after {RETRY_ATTEMPTS} retry attempts.")
    return []


def summarize_article(content):
    """
    Summarize the provided article content using the generative AI model.

    :param content: str, The content of the article to be summarized.

    :return: str, The summarized article text.
    :rtype: str
    """
    prompt = f"Summarize this news article in a comprehensive paragraph, without using bullet points:{content}"
    response = palm.generate_text(**DEFAULTS, prompt=prompt)
    return response.result if response is not None else ""
