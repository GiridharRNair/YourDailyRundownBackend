import os
from datetime import date
from jinja2 import Template
from dotenv import load_dotenv
from pymongo import MongoClient
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from news_summarizer import NewsSummarizer

load_dotenv()

email_sender = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
client = MongoClient(os.environ.get('MONGO_URI'))
users_collection = client.users["users"]

CATEGORY_MAPPING = {
    "realestate": "Real Estate",
    "nyregion": "New York Region",
    "us": "U.S."
}

with open('templates/email_templates/daily_email_template.html', 'r') as file:
    daily_email_template = file.read()
with open('templates/email_templates/article_template.txt', 'r') as file:
    article_template = file.read()


def get_subscribers():
    """
    Retrieve the list of subscribers from the MongoDB collection.

    :returns: A list of dictionaries containing subscriber details.
    :rtype: list
    """
    return [
        {
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'categories': user['categories'],
            'uuid': user['uuid']
        }
        for user in users_collection.find({'validated': 'true'})
    ]


def build_email(uuid, first_name, last_name, categories, articles):
    """
    Build the email content with summarized news articles for the specified categories.

    :param uuid: Unique identifier for each user in the database
    :type uuid: str
    :param first_name: The recipient's first name.
    :type first_name: str
    :param last_name: The recipient's last name.
    :type last_name: str
    :param categories: List of categories to include in the email.
    :type categories: list
    :param articles: A dictionary containing summarized articles categorized by category.
    :type articles: dict

    :returns: The formatted email content.
    :rtype: str
    """
    content = []
    for category in categories:
        formatted_category = CATEGORY_MAPPING.get(category, category)
        content.append(f"<h2>{formatted_category.title()}</h2>")
        for article in articles.get(category, []):
            content.append(Template(article_template).render({
                'image': article["image"],
                'url': article["url"],
                'title': article["title"],
                'content': article["content"],
            }))
    return Template(daily_email_template).render({
        'first_name': first_name,
        'last_name': last_name,
        'content': ''.join(content),
        'uuid': uuid
    })


def send_email(recipent, email_body):
    """
    Send the email containing the summarized news articles to the specified recipient.

    :param recipent: The recipient's email address.
    :type recipent: str
    :param email_body: The HTML content of the email.
    :type email_body: str
    """
    news_letter = Mail(from_email='yourdailyrundown@gmail.com',
                       to_emails=recipent,
                       subject=f'Your Daily Rundown - {str(date.today())}',
                       html_content=email_body)
    try:
        email_sender.send(news_letter)
    except Exception as e:
        print(f"Failed to send email to {recipent}. Error: {str(e)}")


if __name__ == "__main__":
    """
    Deletes all the invalidated users from the database, and runs the daily email distribution script.
    """
    users_collection.delete_many({'validated': 'false'})
    summarized_articles = NewsSummarizer().get_summarized_news()
    for subscriber in get_subscribers():
        email_content = build_email(subscriber['uuid'],
                                    subscriber['first_name'],
                                    subscriber['last_name'],
                                    subscriber['categories'],
                                    summarized_articles)
        send_email(subscriber['email'], email_content)
