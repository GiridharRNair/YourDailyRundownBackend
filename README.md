# YourDailyRundown Back-end

The backend of YourDailyRundown is built using Python and Flask, a lightweight web framework. It interacts with a SQLite database to store user information and preferences. The backend is responsible for handling user registration, storing user data, summarizing news articles using AI, and sending personalized newsletters to subscribers via email.

## Code Structure

The backend code consists of two main files:

1. main.py: This file contains the Flask application, API endpoints, and functions related to user registration, data retrieval, and unsubscription.
</br></br>
2. news_summarizer.py: This file contains the logic for fetching news articles, summarizing them using AI, and sending welcome emails and personalized newsletters to subscribers.

## API Endpoints

The Flask application defines the following API endpoints:

1. POST `/register_user`: This endpoint allows users to register and subscribe to the newsletter. Users need to provide their first name, last name, email, and categories of interest. The data is stored in the SQLite database, and the user receives a welcome email.
   </br></br>
2. GET `/registered_users`: This endpoint retrieves a list of all registered users and their information from the database.
   </br></br>
3. GET `/<email>/unsubscribe`: This endpoint allows users to unsubscribe from the newsletter by providing their email address. The user's data is removed from the database.

## News Summarization

The news_summarizer.py file handles the news summarization process. It uses the google.generativeai library to perform AI-based summarization of news articles. The summarization process involves fetching top headlines from various categories using the Newsdata API and then generating a summary for each category using the AI model.

1. Fetch top headlines for predefined news categories from the Newsdata API.
</br></br>
2. Combine all descriptions from each category into a single text.
</br></br>
3. Use the AI model to generate a summary of the combined text in five comprehensive sentences.
</br></br>
4. Store the summarized news for each category in a dictionary.

## Sending Newsletters

The email_subscribers function in news_summarizer.py is responsible for sending personalized newsletters to subscribers. It fetches the list of registered users from the database, generates a summary of news articles for each user's subscribed categories, and sends a personalized email to each user.

The email content includes a greeting, personalized news summaries for each category, and an unsubscribe link.


## Scheduled Task

To automate the daily newsletter delivery, the news_summarizer.py script is run every day at 8 am CST using PythonAnywhere's scheduled task feature.

## Environment Variables

API keys are stored in a .env file outside the repository. The .env file is loaded using the load_dotenv function, ensuring that sensitive information is kept secure and not exposed in the codebase.