from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from news_summarizer import NewsSummarizer
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests (for development)
DB_NAME = "users.db"
sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))


def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/register_user", methods=["POST"])
def add_user():
    data = request.json
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    email = data.get("email")
    categories = ','.join(item['value'] for item in data.get("category"))
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users (email, first_name, last_name, category)
            VALUES (?, ?, ?, ?)
        """, (email, first_name, last_name, categories))

        cursor.execute("""
            UPDATE users
            SET category = ?,
                first_name = ?,
                last_name = ?
            WHERE email = ?
        """, (categories, first_name, last_name, email))

        conn.commit()

        greeting_email = Mail(
            from_email='yourdailyrundown@gmail.com',
            to_emails=email,
            subject='Your Daily Rundown',
            html_content=(
                f"<p>Hey {first_name} {last_name},</p>\n\n"
                f"<h2>Thanks for joining YourDailyRundown</h2>\n\n"
                f"<p>Welcome to our newsletter! We're thrilled to have you on board.</p>\n\n"
                f"<p>With our newsletter, you'll stay informed about the latest news and updates, all carefully "
                f"curated and summarized to match your interests.</p>\n\n"
                f"<p>Want to personalize your experience even further? You can easily update your preferences and "
                f"name by re-registering for our newsletter. Don't worry about duplicate emails – we've got that "
                f"covered, and all your changes will be recorded seamlessly.</p>\n\n"
                f"<p>If, at any point, you wish to stop receiving our updates, you can simply click the <a "
                f"href='http://127.0.0.1:8000/{email}/unsubscribe'>unsubscribe</a> link provided at the bottom of "
                f"each email.</p>\n\n"
                f"<p>Best regards,<br />Giridhar Nair<br />YourDailyRundown</p>"
            )
        )

        try:
            response = sg.send(greeting_email)
            print(f"Email sent to {email}, status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send email to {email}. Error: {str(e)}")
    return jsonify({"message": "User added successfully"}), 201


@app.route('/registered_users', methods=['GET'])
def get_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM users
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


@app.route('/<email>/unsubscribe')
def unsubscribe(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM users
    WHERE email = ?;
    """, (email,))
    conn.commit()
    cursor.close()
    conn.close()
    return f"Email {email} is removed from the mailing list."


def email_subscribers():
    subscribers = get_users()
    email_content = NewsSummarizer().get_summarized_news()

    for subscriber in subscribers:
        user_id, first_name, last_name, email, categories = subscriber
        categories_list = categories.split(',')
        email_body = f"<h1>Hey {first_name} {last_name}, here is YourDailyRundown!</h1>"
        for category in categories_list:
            email_body += f"<h2>{category.capitalize()}</h2>\n\n"
            email_body += f"<p>{email_content[category.lower()]}</p>"
        email_body += f"<a href='http://127.0.0.1:8000/{email}/unsubscribe'>Want to unsubscribe?</a>"

        # Create a SendGrid email message
        news_letter = Mail(
            from_email='yourdailyrundown@gmail.com',
            to_emails=email,
            subject='Your Daily Rundown',
            html_content=email_body
        )

        try:
            response = sg.send(news_letter)
            print(f"Email sent to {email}, status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send email to {email}. Error: {str(e)}")


if __name__ == "__main__":
    create_table()
    email_subscribers()

    # scheduler = BackgroundScheduler()
    # scheduler.add_job(email_subscribers, 'cron', hour=8)
    # scheduler.start()
    #
    # try:
    #     # Keep the main thread alive while the scheduler runs in the background
    #     while True:
    #         pass
    # except KeyboardInterrupt:
    #     # Shutdown the scheduler gracefully if the user interrupts with Ctrl+C
    #     scheduler.shutdown()
