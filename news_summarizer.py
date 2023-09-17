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

                scraped_content = scrape_content(article_data.get("url"), category)
                if scraped_content:
                    valid_articles_count += 1
                    article_info = {
                        "image": article_data.get("multimedia")[0].get("url"),
                        "title": article_data.get("title"),
                        "url": article_data.get("url"),
                        "content": scraped_content
                    }
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
    :param category: str
    :param article_url: URL of the article.
    :type article_url: str

    :return: Summarized content of the article as a string, or None if summarization fails.
    :rtype: str | None
    """
    try:
        article = NewsPlease.from_url(article_url)
        summarized_content = summarize_article(article.maintext)
        return summarized_content
    except Exception as e:
        print(f"Error summarizing article in {category}: {str(e)}")
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
        response = requests.get(f'https://api.nytimes.com/svc/topstories/v2/{category}.json?api-key={nyt_api_key}')
        if response.status_code == 200:
            return response.json().get('results', [])
        elif response.status_code == 504:
            print(f"Retry attempt {attempt + 1}/{RETRY_ATTEMPTS} - 502 Bad Gateway Error")
            time.sleep(API_REQUEST_INTERVAL)
        else:
            print(f"Retry attempt {attempt + 1}/{RETRY_ATTEMPTS} - {response.status_code} Error")
            return []

    print(f"Unable to fetch articles for {category} after {RETRY_ATTEMPTS} retry attempts.")
    return []


def summarize_article(content):
    """
    Summarize the provided article content using the Google PaLM AI model.

    :param content: The content of the article to be summarized.
    :type content: str

    :return: str, The summarized article text.
    :rtype: str
    """
    prompt = f"Summarize this news article in a comprehensive paragraph, without using bullet points:{content}"
    response = palm.generate_text(**DEFAULTS, prompt=prompt)
    return response.result if response is not None else ""
