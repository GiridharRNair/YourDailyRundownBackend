# YourDailyRundown Backend

Welcome to the YourDailyRundown Backend repository! This backend serves as the core of YourDailyRundown, an email service designed to summarize news articles and deliver them to users.

## Overview

YourDailyRundown streamlines news consumption by gathering articles from various categories through sources such as the New York Times API and The Athletic RSS feed, along with content scraping via [News-Please](https://github.com/fhamborg/news-please). We then provide succinct email summaries, powered by Google's PaLM 2 AI model, and ensure efficient email distribution through Twilio SendGrid. Behind the scenes, our backend handles user registration, verification, updates, and unsubscribing for a seamless user experience.

Live Demo: https://your-daily-rundown.vercel.app/ </br>
Frontend Repo: https://github.com/GiridharRNair/YourDailyRundown

<img src="public/DemoGif.gif" alt="Screenshot">

## Components

### `main.py`

`main.py` is the core Flask application responsible for user registration, validation, updates, and unsubscription. It employs Flask to create API endpoints and interacts with a MongoDB database to manage user data. Here's a brief overview of its key API endpoints:

- `/register_user`: Registers new users by accepting JSON data with user details. It checks for missing fields, duplicates, and sends a validation email if successful.

- `/update_user_preferences`: Allows existing users to update their preferences by providing JSON data with their UUID. It verifies user validation status and sends a confirmation email upon success.

- `/<uuid>/get_user_info`: Retrieves user information based on their UUID, including first name, last name, categories, and validation status.

- `/<uuid>/validate`: Validates a user's email address using their UUID, updates their validation status, and sends a welcome email upon successful validation.

- `/unsubscribe`: Unsubscribes users from email notifications and provides feedback to the developer. It confirms the unsubscription via email.

### `news_summarizer.py`
The `news_summarizer.py` module serves the purpose of summarizing news articles from various categories. It utilizes multiple APIs and external libraries, including the New York Times API, Google's PaLM AI model for text summarization, the `NewsPlease` library for article content extraction, and a custom parser (`TheAthleticParser`) for sports articles. This script summarizes a specified number of articles per category, employing a retry mechanism for resilience against API request errors. It also stores the summarized articles in a MongoDB database, categorized by news category. The module is designed to facilitate automated news aggregation and summarization tasks efficiently.

### `daily_email_distribution.py`
This Python module is responsible for daily email distribution to subscribers, summarizing news articles across categories. It utilizes the SendGrid API for email delivery, interacts with MongoDB to manage user data, and employs the News Summarizer module for article summarization. Key dependencies include `os`, `jinja2`, `pymongo`, and `dotenv`. The module deletes invalidated users from the database and sends personalized emails containing summarized news articles to validated subscribers.

### `the_athletic_parser.py`
The provided Python class, `TheAthleticParser`, is designed for parsing sports articles from The Athletic's RSS feed. It utilizes the `feedparser` library to retrieve and aggregate information about sports articles. The class initializes with an empty list to store article details and provides a method, `get_articles`, which parses the RSS feed, extracts article URLs, titles, and multimedia content (images), and returns this information as a list of dictionaries. This class is a handy tool for extracting sports-related content from The Athletic's feed for further processing or display.

## YAML Files

### `main_yourdailyrundown.yaml`
This YAML file defines a GitHub Actions workflow for building and deploying the Python application to Azure Web App.

### `daily_email_distribution.yaml`
This YAML file defines a GitHub Actions workflow for running the daily_email_distribution.py script on a schedule, daily at 7:30 AM CST (12:30 UTC).

## Environment Variables
To run the YourDailyRundown Backend, you'll need to set the following environment variables:

`AI_API_KEY`= Your Google PaLM AI 2 API Key.

`SENDGRID_API_KEY`=Your SendGrid API Key for Email Distribution.

`NYT_API_KEY`=The New York Times API Key.

`MONGO_URI`=MongoDB Connection String.

`DEV_EMAIL`=My Personal Email Address to Receive Feedback From Users


## Installation

To run this Python project, follow these steps:

1. **Clone the Repository:**
   ```
   git clone https://github.com/GiridharRNair/YourDailyRundownBackend.git
   cd YourDailyRundownBackend/
   ```

2. **Install Dependencies:**
   Use pip to install the required dependencies.
   ```
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Rename `example.env` to `.env`, and fill in the necessary values for environment variables.

4. **Run the Project:**
   Execute the main Python script to start the project.
   ```
   python main.py
   ```

## License
This project is licensed under the MIT License. Feel free to contribute to this project by opening issues or pull requests.

