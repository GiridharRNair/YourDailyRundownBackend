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
    "Nyregion": "NY Region",
    "Us": "U.S."
}


@app.route("/register_user", methods=["POST"])
def add_user():
    """
    Registers a new user by extracting user data from the request JSON.
    Inserts the user's information into the MongoDB database and sends
    a welcome email to the user.

    Returns:
        JSON response indicating the success or failure of the operation.
    """
    try:
        data = request.json
        first_name = data["firstName"]
        last_name = data["lastName"]
        email = data["email"].lower()
        categories = [item['value'] for item in data["category"]]
        add_user_to_database(email, first_name, last_name, categories)
        send_greeting_email(email, first_name, last_name, categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "User added successfully"}), 201


@app.route('/registered_users', methods=['GET'])
def get_users():
    """
    Retrieves a list of registered users from the MongoDB database and
    returns it as a JSON response.

    Returns:
    JSON response containing a list of registered user information.
    """
    user_list = [
        {
            'id': str(user['_id']),
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'category': user['category']
        }
        for user in users_collection.find()
    ]
    return jsonify(user_list)


@app.route('/<email>/unsubscribe')
def unsubscribe(email):
    """
    Handles the unsubscribe process for a user with the provided email address.
    Deletes the user's information from the MongoDB database and renders an
    unsubscribe confirmation page.

    Args:
        email (str): The email address of the user to unsubscribe.

    Returns:
        A rendered template for the unsubscribe confirmation page.
    """
    user = users_collection.find_one_and_delete({'email': email.lower()})
    if user:
        first_name = user['first_name']
        last_name = user['last_name']
        return render_template('unsubscribe_page.html', first_name=first_name, last_name=last_name)
    else:
        return render_template('user_not_found_page.html')


def send_greeting_email(email, first_name, last_name, categories):
    """
    Sends a welcome email to a newly registered user.

    Args:
        email (str): The email address of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        categories (list): A list of user-selected categories.

    Note:
        This function uses the SendGrid API to send emails.

    Returns:
        None
    """
    try:
        formatted_categories = [category.title() for category in categories]
        formatted_categories = [category_mapping.get(category, category) for category in formatted_categories]
        user_categories = ', '.join(formatted_categories[:-1]) + ', and ' + \
                          formatted_categories[-1] if len(formatted_categories) > 1 else formatted_categories[0]
        with open('templates/registration_email.txt', 'r') as file:
            registration_email_content = file.read()
        registration_email_content = registration_email_content.format(first_name, last_name, user_categories, email)
        registration_email = Mail(
            from_email='yourdailyrundown@gmail.com',
            to_emails=email,
            subject='Your Daily Rundown - Welcome!',
            html_content=registration_email_content
        )
        SendGridAPIClient(os.getenv('SENDGRID_API_KEY')).send(registration_email)
    except Exception as e:
        print(f"Failed to send email to {email}. Error: {str(e)}")


def add_user_to_database(email, first_name, last_name, categories):
    """
    Adds a user's information to the MongoDB database.

    Args:
        email (str): The email address of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        categories (list): A list of user-selected categories.

    Returns:
        None
    """
    user_query = {'email': email}
    user_update = {
        '$set': {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'category': categories
        }
    }
    users_collection.update_one(user_query, user_update, upsert=True)


if __name__ == "__main__":
    app.run(debug=True)
