# YourDailyRundown Backend

This is the backend for YourDailyRundown, a news summarization and email delivery service. The backend is responsible for handling user registration, email delivery of summarized news articles, and news article summarization using Google's PaLM AI model.

Frontend Repo: https://github.com/GiridharRNair/YourDailyRundown </br>
Live Demo: https://giridharrnair.github.io/YourDailyRundown/

Example email of the health category:

<img alt="AutomobileCategoryExample" src="public/HealthCategoryExample.png" />

## Architecture

The backend of YourDailyRundown is a Python-based application built using Flask for the web framework. It is responsible for the following main functionalities:

1. **User Registration**: Users can register with their first name, last name, email, and select news categories they are interested in. This information is stored in a MongoDB database.

2. **Email Delivery**: Summarized news articles are sent to users via email on a daily schedule.

3. **News Article Summarization**: The backend retrieves top headlines from the New York Times API for various categories and summarizes these articles using a generative AI model.

4. **Unsubscribe**: Users can unsubscribe from the service by clicking an unsubscribe link in the email. Their information is then removed from the database.

## Components

### `main.py`
This is the main Flask application responsible for handling user registration, email subscription, and unsubscribing users. It utilizes Flask for creating API endpoints and interacts with a MongoDB database to store user information. Here is a summary of its 3 API endpoints:

* `/register_user`: This endpoint registers a new user by extracting user data from the request JSON. It inserts the user's information into the MongoDB database and sends a welcome email to the user.

* `/registered_users`: This endpoint retrieves a list of registered users from the MongoDB database and returns it as a JSON response.

* `/<email>/unsubscribe`: This endpoint handles the unsubscribe process for a user with the provided email address. It deletes the user's information from the MongoDB database and renders an unsubscribe confirmation page.

### `news_summarizer.py`
This script is responsible for summarizing news articles from various categories, sending email newsletters to subscribers, and fetching articles from the New York Times API.

## YAML Files

### `main_yourdailyrundown.yaml`
This YAML file defines a GitHub Actions workflow for building and deploying the Python application to Azure Web App.

### `news_summarizer.yaml`
This YAML file defines a GitHub Actions workflow for running `news_summarizer.py` on a schedule, daily at 8:00 AM CST (13:00 UTC).

## License
This project is licensed under the MIT License. Feel free to contribute to this project by opening issues or pull requests.