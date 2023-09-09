import os
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import Flask, request, jsonify, render_template

load_dotenv()
client = MongoClient(os.environ.get('MONGO_URI'))
users_collection = client.users["users"]
app = Flask(__name__, template_folder="templates")
CORS(app)
category_mapping = {
    "Realestate": "Real Estate",
    "Nyregion": "New York Region",
    "Us": "U.S."
}

with open('templates/registration_email.txt', 'r') as file:
    registration_email_template = file.read()
with open('templates/validate_email.txt', 'r') as file:
    validate_user_email_template = file.read()
with open('templates/updated_preferences_email.txt', 'r') as file:
    updated_preferences_email_template = file.read()


@app.route("/register_user", methods=["POST"])
def add_user():
    """
    Register a new user or update existing user preferences based on POST data.

    :returns: JSON response indicating success or error
    :rtype: dict
    """
    try:
        data = request.json
        email = data["email"].lower()
        first_name = data["firstName"]
        last_name = data["lastName"]
        categories = [item['value'] for item in data["category"]]
        user = users_collection.find_one({'email': email})
        if user and user['validated'] == 'true':
            update_existing_user_preferences(email, categories)
            send_updated_preferences_email(email, first_name, last_name, categories)
            return jsonify({"message": "User's preferences updated successfully"}), 201
        else:
            add_new_user_to_database(email, first_name, last_name, categories)
            send_validation_email(first_name, last_name, email)
            return jsonify({"message": "Check your email!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/<email>/validate', methods=['GET'])
def validate_user(email):
    """
    Validate a user's email address.

    :param email: User's email address
    :type email: str
    :returns: HTML response for validation or user not found
    :rtype: str
    """
    user = users_collection.find_one({'email': email})
    if user:
        first_name = user['first_name']
        last_name = user['last_name']
        categories = user['category']
        user_update = {'$set': {'validated': 'true'}}
        users_collection.update_one({'email': email}, user_update, upsert=True)
        send_greeting_email(email, first_name, last_name, categories)
        return render_template('validate_user_page.html', first_name=first_name, last_name=last_name)
    else:
        return render_template('user_not_found_page.html')


@app.route('/<email>/unsubscribe')
def unsubscribe(email):
    """
    Unsubscribe a user from email notifications.

    :param email: User's email address
    :type email: str
    :returns: HTML response for unsubscribe or user not found
    :rtype: str
    """
    user = users_collection.find_one_and_delete({'email': email.lower()})
    if user:
        first_name = user['first_name']
        last_name = user['last_name']
        return render_template('unsubscribe_page.html', first_name=first_name, last_name=last_name)
    else:
        return render_template('user_not_found_page.html')


def send_updated_preferences_email(email, first_name, last_name, categories):
    """
    Email notify a user of updated preferences.

    :param email: User's email address
    :type email: str
    :param first_name: User's first name
    :type first_name: str
    :param last_name: User's last name
    :type last_name: str
    :param categories: User's updated categories
    :type categories: list
    """
    try:
        user_categories = format_categories(categories)
        updated_preferences_content \
            = updated_preferences_email_template.format(first_name, last_name, user_categories, email)
        updated_preferences_email = Mail(
            from_email='yourdailyrundown@gmail.com',
            to_emails=email,
            subject='Your Daily Rundown - Preferences Updated!',
            html_content=updated_preferences_content
        )
        SendGridAPIClient(os.getenv('SENDGRID_API_KEY')).send(updated_preferences_email)
    except Exception as e:
        print(f"Failed to send email to {email}. Error: {str(e)}")


def send_validation_email(first_name, last_name, email):
    """
    Send a validation email to a user.

    :param first_name: User's first name
    :type first_name: str
    :param last_name: User's last name
    :type last_name: str
    :param email: User's email address
    :type email: str
    """
    try:
        validate_user_email_content = validate_user_email_template.format(first_name, last_name, email)
        validate_user_email = Mail(
            from_email='yourdailyrundown@gmail.com',
            to_emails=email,
            subject='Your Daily Rundown - One More Step!',
            html_content=validate_user_email_content
        )
        SendGridAPIClient(os.getenv('SENDGRID_API_KEY')).send(validate_user_email)
    except Exception as e:
        print(f"Failed to send email to {email}. Error: {str(e)}")


def send_greeting_email(email, first_name, last_name, categories):
    """
    Send a welcome email to a user.

    :param email: User's email address
    :type email: str
    :param first_name: User's first name
    :type first_name: str
    :param last_name: User's last name
    :type last_name: str
    :param categories: User's categories of interest
    :type categories: list
    """
    try:
        user_categories = format_categories(categories)
        registration_email_content = registration_email_template.format(first_name, last_name, user_categories, email)
        registration_email = Mail(
            from_email='yourdailyrundown@gmail.com',
            to_emails=email,
            subject='Your Daily Rundown - Welcome!',
            html_content=registration_email_content
        )
        SendGridAPIClient(os.getenv('SENDGRID_API_KEY')).send(registration_email)
    except Exception as e:
        print(f"Failed to send email to {email}. Error: {str(e)}")


def add_new_user_to_database(email, first_name, last_name, categories):
    """
    Add a new user to the database.

    :param email: User's email address
    :type email: str
    :param first_name: User's first name
    :type first_name: str
    :param last_name: User's last name
    :type last_name: str
    :param categories: User's categories of interest
    :type categories: list
    """
    user_query = {'email': email}
    user_update = {
        '$set': {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'category': categories,
            'validated': 'false'
        }
    }
    users_collection.update_one(user_query, user_update, upsert=True)


def update_existing_user_preferences(email, categories):
    """
    Update the preferences of an existing user in the database.

    :param email: User's email address
    :type email: str
    :param categories: User's updated categories of interest
    :type categories: list
    """
    user_query = {'email': email}
    user_update = {
        '$set': {
            'category': categories,
        }
    }
    users_collection.update_one(user_query, user_update, upsert=True)


def format_categories(categories):
    """
    Format a list of categories.

    :param categories: List of categories
    :type categories: list
    :returns: Formatted string of categories
    :rtype: str
    """
    formatted_categories = [category_mapping.get(category.title(), category.title()) for category in categories]
    if len(formatted_categories) > 1:
        return ', '.join(formatted_categories[:-1]) + ' and ' + formatted_categories[-1]
    elif formatted_categories:
        return formatted_categories[0]
    else:
        return ""


if __name__ == "__main__":
    app.run()
