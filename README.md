# YourDailyRundown Back-end

The backend of YourDailyRundown is built with Python and Flask, a lightweight web framework, and deployed using PythonAnywhere. It interacts with an SQLite database to store user information and preferences. Its tasks include user registration, data storage, AI-powered news article summarization, and personalized newsletter delivery via email. 

[Frontend Repo](https://github.com/GiridharRNair/YourDailyRundown)

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

The news_summarizer.py module is responsible for conducting news summarization utilizing advanced AI capabilities. Powered by the google.generativeai library, it orchestrates the process of generating concise news summaries from articles. Here's a step-by-step overview of how the summarization process takes place:

1. **Fetching Top Headlines**:
   The module interacts with the Newsdata API to retrieve the latest top 3 headlines for predefined news categories. Each category, such as business, politics, entertainment, general, health, science, sports, technology, and world, is processed individually.
</br></br>
2. **Article Extraction**:
   For each retrieved headline, the module extracts article content from the provided link. This content is acquired using the World News API. The extraction process ensures that only valid articles with meaningful content are considered for summarization.
</br></br>
3. **Summarization Generation**:
   The AI model, configured with parameters like model type, temperature, candidate count, and more, generates a comprehensive summary for the collected articles. The content is summarized into a cohesive paragraph, with the goal of condensing the key points and highlights.
</br></br>
4. **Summarized News Storage**:
   The generated summaries for each category are stored in a dictionary. This dictionary maintains an organized record of the summarized news content for future use.
</br></br>
5. **Subscriber Notification**:
   The summarized news content is then used to create personalized newsletters for subscribers.  Using the SendGrid API, the module dispatches the crafted newsletters to the subscribers' email addresses based on their intrests. Each email includes a link allowing subscribers to easily unsubscribe from future notifications if desired. The email_subscribers function in news_summarizer.py is responsible for sending personalized newsletters to subscribers. It fetches the list of registered users from the database, generates a summary of news articles for each user's subscribed categories, and sends a personalized email to each user.

This comprehensive workflow showcases the integration of AI-based summarization, news article extraction, and efficient delivery of personalized news summaries to subscribers' inboxes. The entire process is orchestrated within the news_summarizer.py module, facilitating a seamless and informative news summarization experience.

## Scheduled Task

To automate the daily newsletter delivery, the news_summarizer.py script is run every day at 8 am CST using PythonAnywhere's scheduled task feature.

## Environment Variables

API keys are stored in a .env file outside the repository. The .env file is loaded using the load_dotenv function, ensuring that sensitive information is kept secure and not exposed in the codebase.