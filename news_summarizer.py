import os
import time
import requests
from datetime import date
import google.generativeai as palm
from dotenv import load_dotenv
from pymongo import MongoClient
from newsplease import NewsPlease
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient

load_dotenv()

ARTICLE_COUNT = 3
API_REQUEST_INTERVAL = 8

palm.configure(api_key=os.getenv('AI_API_KEY'))
nyt_api_key = os.getenv('NYT_API_KEY')

email_sender = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
client = MongoClient(os.environ.get('MONGO_URI'))
users_collection = client.users["users"]

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

CATEGORY_MAPPING = {
    "realestate": "Real Estate",
    "nyregion": "NY Region",
    "us": "U.S."
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
        """
        self.get_top_headlines_for_categories()
        return self.categories_dict


def summarize_article(content):
    """
    Summarize the provided article content using the generative AI model.

    Args:
        content (str): The content of the article to be summarized.

    Returns:
        str: The summarized article text.
    """
    prompt = f"Summarize this news article in a comprehensive paragraph, without using bullet points:{content}"
    response = palm.generate_text(**DEFAULTS, prompt=prompt)
    return response.result if response is not None else ""


def email_subscribers():
    """
    Send summarized news articles to subscribers via email.
    """
    summarized_articles = NewsSummarizer().get_summarized_news()
    for subscriber in get_subscribers():
        recipent = subscriber['email']
        email_body = build_email(recipent,
                                 subscriber['first_name'],
                                 subscriber['last_name'],
                                 subscriber['category'],
                                 summarized_articles)
        send_email(recipent, email_body)


def get_subscribers():
    """
    Retrieve the list of subscribers from the MongoDB collection.

    Returns:
        list: A list of dictionaries containing subscriber details.
    """
    return [
        {
            'id': str(user['_id']),
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'category': user['category']
        }
        for user in users_collection.find()
    ]


def build_email(email, first_name, last_name, categories, articles):
    """
    Build the email content with summarized news articles for the specified categories.

    Args:
        email (str): The recipient's email address.
        first_name (str): The recipient's first name.
        last_name (str): The recipient's last name.
        categories (list): List of categories to include in the email.
        articles (dict): A dictionary containing summarized articles categorized by category.

    Returns:
        str: The formatted email content.
    """
    email_body = f"<p>Hey {first_name} {last_name}, here is YourDailyRundown!</p>"
    for category in categories:
        formatted_category = CATEGORY_MAPPING.get(category, category)
        email_body += f"<h2>{formatted_category.title()}</h2>\n\n"
        for article in articles.get(category, []):
            email_body += f'<a href="{article["url"]}">{article["title"]}</a><br/>{article["content"]}<br/><br/>'
    email_body += f"<a href='https://yourdailyrundown.azurewebsites.net/{email}/unsubscribe'>Want to unsubscribe?</a>"
    email_body += (
        "<br/><br/>Want to change your preferences? " 
        "Just <a href='https://giridharrnair.github.io/YourDailyRundown/'>re-register for our newsletter</a>. "
        "Don't worry about duplicate emails – we've got that covered, and all your changes will be "
        "recorded seamlessly.</p>"
    )
    return email_body


def send_email(recipent, email_body):
    """
    Send the email containing the summarized news articles to the specified recipient.

    Args:
        :param email_body: The recipient's email address.
        :param recipent: The HTML content of the email.
    """
    news_letter = Mail(from_email='yourdailyrundown@gmail.com',
                       to_emails=recipent,
                       subject='Your Daily Rundown - ' + str(date.today()),
                       html_content=email_body)
    try:
        email_sender.send(news_letter)
        print(f"Successfully sent Email to {recipent}")
    except Exception as e:
        print(f"Failed to send email to {recipent}. Error: {str(e)}")


def extract_article_details(article_url, article_title, category):
    """
    Extract article details, summarize the content, and return a dictionary with relevant information.

    Args:
        article_url (str): URL of the article.
        article_title (str): Title of the article.
        category (str): Category of the article.

    Returns:
        dict: A dictionary containing title, URL, and summarized content of the article.
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

    Args:
        category (str): The category for which to fetch articles.

    Returns:
        list: A list of dictionaries containing article information.
    """
    response = requests.get(f'https://api.nytimes.com/svc/topstories/v2/{category}.json?api-key={nyt_api_key}')
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Error fetching articles for {category}: {response.status_code}")
        return []


if __name__ == "__main__":
    email_subscribers()
