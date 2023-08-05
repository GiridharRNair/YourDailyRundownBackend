import os
import google.generativeai as palm
import requests
from dotenv import load_dotenv
from main import get_users
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient

project_folder = os.path.expanduser('/home/GiridharNair/mysite')
load_dotenv(os.path.join(project_folder, '.env'))

palm.configure(api_key=os.getenv('AI_API_KEY'))
news_api_key = os.getenv('NEWS_API_KEY')
defaults = {
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
    def __init__(self):
        self.categories = ['business', 'politics', 'entertainment', 'general', 'health',
                           'science', 'sports', 'technology', 'world']
        self.categories_dict = {category: [] for category in self.categories}

    def get_top_headlines_for_categories(self):
        for category in self.categories:
            response = requests.get(f'https://newsdata.io/api/1/news?apikey={news_api_key}&q'
                                    f'={category}&country=us&language=en').json()
            for article in range(len(response["results"])):
                if response["results"][article]["description"]:
                    self.categories_dict[category].append(response["results"][article]["description"])
            news_descriptions = summarize_article(".".join(self.categories_dict[category]))
            self.categories_dict[category] = news_descriptions.replace("**", "")

    def get_summarized_news(self):
        self.get_top_headlines_for_categories()
        return self.categories_dict


def summarize_article(content):
    prompt = f"""Summarize this news article in a comprehensive paragraph,
    without using bullet points:{content}"""
    response = palm.generate_text(
        **defaults,
        prompt=prompt
    )
    if response is not None:
        return response.result
    else:
        return ""


def email_subscribers():
    subscribers = get_users()
    email_content = NewsSummarizer().get_summarized_news()

    for subscriber in subscribers:
        user_id, first_name, last_name, email, categories = subscriber
        categories_list = categories.split(',')
        email_body = f"<p>Hey {first_name} {last_name}, here is YourDailyRundown!</p>"
        for category in categories_list:
            email_body += f"<h2>{category.capitalize()}</h2>\n\n"
            email_body += f"<p>{email_content[category.lower()]}</p>"
        email_body += f"<a href='http://127.0.0.1:8000/{email}/unsubscribe'>Want to unsubscribe?</a>"

        news_letter = Mail(
            from_email='yourdailyrundown@gmail.com',
            to_emails=email,
            subject='Your Daily Rundown',
            html_content=email_body
        )

        try:
            response = SendGridAPIClient(os.getenv('SENDGRID_API_KEY')).send(news_letter)
            print(f"Email sent to {email}, status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send email to {email}. Error: {str(e)}")


if __name__ == "__main__":
    email_subscribers()
