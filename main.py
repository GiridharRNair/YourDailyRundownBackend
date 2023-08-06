from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

project_folder = os.path.expanduser('/home/GiridharNair/mysite')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

app = Flask(__name__, template_folder="/home/GiridharNair/mysite/templates")
CORS(app)  # Allow cross-origin requests (for development)
DB_NAME = "/home/GiridharNair/mysite/users.db"


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
    email = data.get("email").lower()
    categories = ','.join(item['value'] for item in data.get("category"))
    with sqlite3.connect(DB_NAME) as conn:
        try:
            add_user_to_database(conn, email, first_name, last_name, categories)
            send_greeting_email(email, first_name, last_name, categories)
        except Exception as e:
            return jsonify({"error": e}), 500
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
    SELECT first_name, last_name
    FROM users
    WHERE email = ?;
    """, (email.lower(),))

    result = cursor.fetchone()
    if result:
        first_name, last_name = result

        cursor.execute("""
        DELETE FROM users
        WHERE email = ?;
        """, (email.lower(),))

        conn.commit()
        cursor.close()
        conn.close()

        return render_template('unsubscribe_page.html', first_name=first_name, last_name=last_name)
    else:
        cursor.close()
        conn.close()
        return render_template('user_not_found_page.html')


def send_greeting_email(email, first_name, last_name, categories):
    try:
        categories_str = ', '.join(categories) if categories else 'general news'
        greeting_email = Mail(
            from_email='yourdailyrundown@gmail.com',
            to_emails=email,
            subject='Your Daily Rundown - Welcome!',
            html_content=(
                f"<p>Hey {first_name} {last_name},</p>\n\n"
                f"<h2>Thanks for joining YourDailyRundown</h2>\n\n"
                f"<p>Welcome to our newsletter! We're thrilled to have you on board.</p>\n\n"
                f"<p>With our newsletter, you'll stay informed about the latest news and updates, all carefully "
                f"curated and summarized to match your interests in {categories_str}.</p>\n\n"
                f"<p>Want to personalize your experience even further? You can easily update your preferences and "
                f"name by re-registering for our newsletter. Don't worry about duplicate emails – we've got that "
                f"covered, and all your changes will be recorded seamlessly.</p>\n\n"
                f"<p>If, at any point, you wish to stop receiving our updates, you can simply click the <a "
                f"href='https://giridharnair.pythonanywhere.com/{email}/unsubscribe'>unsubscribe</a> link provided at "
                f"the bottom of"
                f"each email.</p>\n\n"
                f"<p>Best regards,<br />Giridhar Nair<br />YourDailyRundown</p>"
            )
        )
        response = SendGridAPIClient(os.getenv('SENDGRID_API_KEY')).send(greeting_email)
        print(f"Email sent to {email}, status code: {response.status_code}")
    except Exception as e:
        print(f"Failed to send email to {email}. Error: {str(e)}")
        raise


def add_user_to_database(conn, email, first_name, last_name, categories):
    try:
        with conn:
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
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        raise


if __name__ == "__main__":
    create_table()

    app.run()  # Start the Flask application
