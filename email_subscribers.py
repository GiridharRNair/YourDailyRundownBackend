import os
from datetime import date
from dotenv import load_dotenv
from pymongo import MongoClient
from news_summarizer import NewsSummarizer
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient

load_dotenv()

email_sender = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
client = MongoClient(os.environ.get('MONGO_URI'))
users_collection = client.users["users"]

CATEGORY_MAPPING = {
    "realestate": "Real Estate",
    "nyregion": "New York Region",
    "us": "U.S."
}


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

    :returns: A list of dictionaries containing subscriber details.
    :rtype: list
    """
    users_collection.delete_many({'validated': 'false'})
    return [
        {
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'category': user['category']
        }
        for user in users_collection.find({'validated': 'true'})
    ]


def build_email(email, first_name, last_name, categories, articles):
    """
    Build the email content with summarized news articles for the specified categories.

    :param email: The recipient's email address.
    :type email: str
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

    :param recipent: The recipient's email address.
    :type recipent: str
    :param email_body: The HTML content of the email.
    :type email_body: str
    """
    news_letter = Mail(from_email='yourdailyrundown@gmail.com',
                       to_emails=recipent,
                       subject='Your Daily Rundown - ' + str(date.today()),
                       html_content=email_body)
    try:
        email_sender.send(news_letter)
    except Exception as e:
        print(f"Failed to send email to {recipent}. Error: {str(e)}")


if __name__ == "__main__":
    email_subscribers()
