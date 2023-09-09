# YourDailyRundown Backend


This serves as the backend for YourDailyRundown, an email service that summarizes news articles and delivers them. The backend has the crucial tasks of managing user registration and validation, as well as sending out these summaries, which are generated using Google's PaLM AI model. The news articles are gathered from the New York Times API and extracted using [News-Please](https://github.com/fhamborg/news-please).

Frontend Repo: https://github.com/GiridharRNair/YourDailyRundown </br>
Live Demo: https://giridharrnair.github.io/YourDailyRundown/

Example email of the health category:

<img alt="AutomobileCategoryExample" src="public/HealthCategoryExample.png" />

## Architecture

The backend of YourDailyRundown is a Python-based application built using Flask for the web framework. It is responsible for the following main functionalities:

1. **User Registration**: Users can register with their first name, last name, email, and select news categories they are interested in. This information is stored in a MongoDB database after user validation.

2. **Email Delivery**: Summarized news articles are sent to users via email on a daily schedule at 8 AM CST (13:00 UTC).

3. **News Article Summarization**: The backend retrieves top headlines from the New York Times API for various categories and summarizes these articles using a Google's PaLM AI.

4. **Unsubscribe**: Users can unsubscribe from the service by clicking an unsubscribe link in the email. Their information is then removed from the database.

## Components

### `main.py`
`main.py` is the main Flask application responsible for handling user registration, validation, and unsubscription. It utilizes Flask to create API endpoints and interacts with a MongoDB database to store user information. Here's an overview of its API endpoints:

* `/register_user`: This endpoint registers a new user by extracting user data from the request JSON. It inserts the user's information into the MongoDB database and sends an email notification to validate the user's email. If the user's email exists in the database, the user's preferences will be updated from the request JSON and an email notification will be sent regarding the changes.


* `/<email>/validate`: This endpoint handles the email validation process for a user with the provided email address. It updates the user's validation status in the database, sends a greeting email to the user, and renders a validation success confirmation page.


* `/<email>/unsubscribe`: This endpoint handles the unsubscribe process for a user with the provided email address. It deletes the user's information from the MongoDB database and renders an unsubscribe confirmation page.

### `news_summarizer.py`
`news_summarizer.py` is responsible for summarizing, using Google's PaLM AI, news articles from various categories sourced from the New York Times API, scraped using [News-Please](https://github.com/fhamborg/news-please).

### `email_subscribers.py`
`email_subscribers.py` sends the summarized news articles from `news_summarizer.py` to subscribers via email. It retrieves the list of validated subscribers from the MongoDB collection and builds the email content with summarized news articles for the specified categories.

## YAML Files

### `main_yourdailyrundown.yaml`
This YAML file defines a GitHub Actions workflow for building and deploying the Python application to Azure Web App.

### `email_subscribers.yaml`
This YAML file defines a GitHub Actions workflow for running `email_subscribers.py` on a schedule, daily at 8:00 AM CST (13:00 UTC).

## License
This project is licensed under the MIT License. Feel free to contribute to this project by opening issues or pull requests.