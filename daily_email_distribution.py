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

EMAIL_CLOSER = (
    """
    <p>Interested in customizing your experience? Click here to update your preferences and name: 
    <a href='https://giridharrnair.github.io/YourDailyRundown/{}/'>Update Preferences</a>. 
    Rest assured, you won't receive duplicate emails, and all your changes will be seamlessly recorded.</p>
    
    <a href='https://yourdailyrundown.azurewebsites.net/{}/unsubscribe'>Want to unsubscribe?</a>
    """
)


def email_subscribers():
    """
    Send summarized news articles to subscribers via email.
    """
    summarized_articles = NewsSummarizer().get_summarized_news()
    for subscriber in get_subscribers():
        email_body = build_email(subscriber['uuid'],
                                 subscriber['first_name'],
                                 subscriber['last_name'],
                                 subscriber['categories'],
                                 summarized_articles)
        send_email(subscriber['email'], email_body)


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
    email_body = f"<p>Hey {first_name} {last_name}, here is YourDailyRundown!</p>"
    for category in categories:
        formatted_category = CATEGORY_MAPPING.get(category, category)
        email_body += f"<h2>{formatted_category.title()}</h2>\n\n"
        for article in articles.get(category, []):
            email_body += f'<a href="{article["url"]}">{article["title"]}</a><br/>{article["content"]}<br/><br/>'
    email_body += EMAIL_CLOSER.format(uuid)
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
