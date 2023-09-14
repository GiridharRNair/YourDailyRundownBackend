import os
import shortuuid
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
with open('templates/user_unsubscribe_email.txt', 'r') as file:
    user_unsubscribe_email_template = file.read()
with open('templates/feedback_email.txt', 'r') as file:
    user_feedback_email_template = file.read()


@app.route("/register_user", methods=["POST"])
def register_user():
    """
    Registers a new user based on POST data.

    :returns: JSON response indicating success or error
    :rtype: dict
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        email = data["email"].lower()
        first_name = data["firstName"].strip().title()
        last_name = data["lastName"].strip().title()
        categories = [item['value'] for item in data["category"]]

        if not email or not first_name or not last_name or not categories:
            return jsonify({"error": "Missing required fields"}), 400

        user = users_collection.find_one({'email': email})

        if not user or user['validated'] == 'false':
            uuid = shortuuid.uuid()
            user_update = {
                '$set': {
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'categories': categories,
                    'uuid': uuid,
                    'validated': 'false'
                }
            }
            users_collection.update_one({'email': email}, user_update, upsert=True)
            validate_user_email_content = validate_user_email_template.format(first_name, last_name, uuid)
            send_email('Your Daily Rundown - One More Step!', email, validate_user_email_content)
            return jsonify({"message": "Check your email!"}), 201
        else:
            return jsonify({"error": "Email already in use"}), 409

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/update_user_preferences", methods=["POST"])
def update_existing_user():
    """
    Update existing user preferences based on POST data.

    :return: JSON response indicating success or error
    :rtype: dict
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        uuid = data['uuid']
        first_name = data['firstName'].strip().title()
        last_name = data['lastName'].strip().title()
        new_categories = [item['value'] for item in data["category"]]

        if not uuid or not first_name or not last_name or not new_categories:
            return jsonify({"error": "Missing required fields"}), 400

        user = users_collection.find_one({'uuid': uuid})

        if user:
            if user['validated'] == 'true':
                user_update = {
                    '$set': {
                        'first_name': first_name,
                        'last_name': last_name,
                        'categories': new_categories,
                    }
                }
                users_collection.update_one({'uuid': uuid}, user_update, upsert=True)
                updated_preferences_email_content = updated_preferences_email_template.format(
                    first_name, last_name, format_categories(new_categories), uuid
                )
                send_email(
                    'Your Daily Rundown - Preferences Updated!', user['email'], updated_preferences_email_content
                )
                return jsonify({"message": f"{first_name}'s preferences updated successfully"}), 200
            else:
                return jsonify({"error": "User is not validated"}), 401
        else:
            return jsonify({"error": "User does not exist"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/<uuid>/get_user_info', methods=['GET'])
def get_user_info(uuid):
    """
    Get user information, including first name, last name, and categories, for a validated user.

    :param uuid: The UUID of the user to retrieve information for.
    :type uuid: str
    :return: JSON response containing user information or an error message.
    :rtype: dict
    """
    try:
        user = users_collection.find_one({'uuid': uuid})

        if user:
            user_info = {
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'categories': user['categories'],
                'validated': user['validated']
            }
            return jsonify({'user_info': user_info}), 200
        else:
            return jsonify({"error": "User does not exist"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/<uuid>/validate', methods=['GET'])
def validate_user(uuid):
    """
    Validate a user's email address.

    :param uuid: Unique identifier for each user in the database
    :type uuid: str
    :returns: HTML response for validation or user not found
    :rtype: str
    """
    try:
        user = users_collection.find_one({'uuid': uuid})

        if user:
            if user['validated'] == 'false':
                user_update = {'$set': {'validated': 'true'}}
                users_collection.update_one({'uuid': uuid}, user_update, upsert=True)
                registration_email_content = registration_email_template.format(
                    user['first_name'], user['last_name'], format_categories(user['categories']), uuid
                )
                send_email('Your Daily Rundown - Welcome!', user['email'], registration_email_content)
                return render_template('validate_user_page.html',
                                       first_name=user['first_name'],
                                       last_name=user['last_name'])
            else:
                return render_template('user_already_validated.html',
                                       first_name=user['first_name'],
                                       last_name=user['last_name'])
        else:
            return render_template('user_not_found_page.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    """
    Unsubscribe a user from email notifications and sends the user's feedback to the developer.

    :returns: JSON response indicating success or error
    :rtype: str
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        user = users_collection.find_one_and_delete({'uuid': data['uuid']})

        if user:
            first_name = user['first_name']
            unsubscription_email_content = user_unsubscribe_email_template.format(user['first_name'], user['last_name'])
            send_email(
                'Your Daily Rundown - Unsubscription Confirmation', user['email'], unsubscription_email_content
            )
            if data["feedback"]:
                user_feedback_email_content = user_feedback_email_template.format(
                    user['first_name'], user['last_name'], user['email'], data['feedback']
                )
                send_email('YourDailyRundown - Feedback', os.environ.get('DEV_EMAIL'), user_feedback_email_content)
            return jsonify({'message': f'{first_name} is successfully unsubscribed'}), 200
        else:
            return jsonify({"error": "User does not exist"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def send_email(subject, recipient, email_content):
    """
    Send an email using the SendGrid API.

    :param subject: The subject of the email.
    :type subject: str
    :param recipient: The recipient's email address.
    :type recipient: str
    :param email_content: The HTML content of the email.
    :type email_content: str
    """
    try:
        registration_email = Mail(
            from_email='yourdailyrundown@gmail.com',
            to_emails=recipient,
            subject=subject,
            html_content=email_content
        )
        SendGridAPIClient(os.getenv('SENDGRID_API_KEY')).send(registration_email)
    except Exception as e:
        print(f"Failed to send email to {recipient}. Error: {str(e)}")


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
