# YourDailyRundown Backend

Welcome to the YourDailyRundown Backend repository! This backend serves as the core of YourDailyRundown, an email service designed to summarize news articles and deliver them to users. In this README, we'll provide an overview of the project, its architecture, components, environment variables, and licensing information.

## Overview

YourDailyRundown simplifies news consumption by aggregating articles from different categories and delivering concise versions via email. Our backend manages user registration, validation, updates, and unsubscription. We leverage Google's PaLM 2 AI model for article summarization and rely on Twilio SendGrid for email distribution. Our news sources include the New York Times API and scraping via [News-Please](https://github.com/fhamborg/news-please).

Live Demo: https://your-daily-rundown.vercel.app/ </br>
Frontend Repo: https://github.com/GiridharRNair/YourDailyRundown 

<img src="public/DemoGif.gif" alt="Screenshot">

## Architecture

The backend of YourDailyRundown is a Python-based application built using the Flask web framework. It is responsible for the following main functionalities:

1. **User Registration**: Users can register with their first name, last name, email, and select news categories they are interested in. This information is stored in a MongoDB database after user validation.


2. **News Article Summarization**: To provide users with a concise overview of the day's top headlines, the backend retrieves news articles from the New York Times API across 20 categories. It then leverages Google's PaLM 2 AI to generate accurate and informative article summaries. This summarization process helps users quickly grasp the key points of each article.


3. **Email Delivery**: Send subscribers custom emails, daily at 8 AM CST (13:00 UTC), by retrieving subscriber data, summarizing news articles based on their selected categories (from the previous step), creates HTML email content, and utilizes the SendGrid service for email delivery. 


4. **Unsubscribe**: For users who wish to discontinue the service, YourDailyRundown offers a straightforward unsubscribe option. By clicking the unsubscribe button provided in the daily email, users can easily opt out of receiving further newsletters. The backend ensures that their information is promptly removed from the database.

## Components

### `main.py`
`main.py` is the main Flask application responsible for handling user registration, validation, updates, and unsubscription. It utilizes Flask to create API endpoints and interacts with a MongoDB database to store user information. Here's an overview of its API endpoints:

* `/register_user`: Registers a new user by accepting JSON data containing user details. It checks for missing fields, duplicates, and sends a validation email if successful.


* `/update_user_preferences`: Allows existing users to update their preferences by providing JSON data with their UUID. It checks if the user is validated and sends a confirmation email.


* `/<uuid>/get_user_info`: Retrieves user information based on their UUID, including first name, last name, categories, and validation status.


* `/<uuid>/validate`: Validates a user's email address using their UUID, updates their validation status, and sends a welcome email upon successful validation.


* `/unsubscribe`: Unsubscribes users from email notifications and sends feedback to the developer. It confirms the unsubscription via email.

### `news_summarizer.py`
Summarizes news articles across diverse categories by leveraging the New York Times API to source top articles, employing the [News-Please](https://github.com/fhamborg/news-please) library and a Google AI model (PaLM) for content scraping and summarization. Summarized articles are organized in a dictionary, categorized into 20 news categories. The code offers configuration settings, adeptly handles API request errors, and incorporates retry mechanisms for managing API request failures. Key parameters, such as the number of articles to fetch and retry attempts, are customizable constants situated at the script's outset. Furthermore, it adeptly manages API keys and environmental variables through the dotenv library.

### `daily_email_distribution.py`
This Python script loads environment variables, connects to a MongoDB database, and sends daily personalized email newsletters to validated subscribers. It retrieves subscriber data, summarizes news articles based on their selected categories (via `news_summarizer.py`), creates HTML email content, and utilizes the SendGrid service for email delivery. Invalidated users are initially removed from the database, followed by the creation and dispatch of tailored emails containing summarized news articles to each subscriber's email address.

## YAML Files

### `main_yourdailyrundown.yaml`
This YAML file defines a GitHub Actions workflow for building and deploying the Python application to Azure Web App.

### `daily_email_distribution.yaml`
This YAML file defines a GitHub Actions workflow for running the daily_email_distribution.py script on a schedule, daily at 8:00 AM CST (13:00 UTC).

## Environment Variables
To run the YourDailyRundown Backend, you'll need to set the following environment variables:

`AI_API_KEY`= Your Google PaLM AI 2 API Key.

`SENDGRID_API_KEY`=Your SendGrid API Key for Email Distribution.

`NYT_API_KEY`=The New York Times API Key.

`MONGO_URI`=MongoDB Connection String.

`DEV_EMAIL`=My Personal Email Address to Receive Feedback From Users

## License
This project is licensed under the MIT License. Feel free to contribute to this project by opening issues or pull requests.