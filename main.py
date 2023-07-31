from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from news_summarizer import NewsSummarizer
import resend
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])  # Allow cross-origin requests (for development)
DB_NAME = "users.db"
resend.api_key = os.getenv('RESEND_API_KEY')


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
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            cursor.execute("""
            DELETE FROM users
            WHERE email = ?;
            """, (email,))
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, category)
            VALUES (?, ?, ?, ?)
        """, (first_name, last_name, email, categories))

        conn.commit()
    return jsonify({"message": "User added successfully"}).headers.add('Access-Control-Allow-Origin', '*'), 201


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
        email_body += f"<a href='http://127.0.0.1:5000/{email}/unsubscribe'>Want to unsubscribe?</a>"
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": email,
            "subject": "Your Daily Rundown",
            "html": email_body
        })


if __name__ == "__main__":
    create_table()
    # email_subscribers()

    scheduler = BackgroundScheduler()
    scheduler.add_job(email_subscribers, 'cron', hour=8)
    scheduler.start()

    try:
        # Keep the main thread alive while the scheduler runs in the background
        while True:
            pass
    except KeyboardInterrupt:
        # Shutdown the scheduler gracefully if the user interrupts with Ctrl+C
        scheduler.shutdown()
