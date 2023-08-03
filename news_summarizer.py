import os
import google.generativeai as palm
import requests

palm.configure(api_key=os.getenv('AI_API_KEY'))
news_api_key = os.getenv('NEWS_API_KEY')
defaults = {
    'model': 'models/text-bison-001',
    'temperature': 0.6,
    'candidate_count': 1,
    'top_k': 40,
    'top_p': 0.95,
    'max_output_tokens': 1024,
    'stop_sequences': [],
    'safety_settings': [{"category": "HARM_CATEGORY_DEROGATORY", "threshold": 1},
                        {"category": "HARM_CATEGORY_TOXICITY", "threshold": 1},
                        {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 2},
                        {"category": "HARM_CATEGORY_SEXUAL", "threshold": 2},
                        {"category": "HARM_CATEGORY_MEDICAL", "threshold": 2},
                        {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 2}],
}


class NewsSummarizer:
    def __init__(self):
        self.categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
        self.categories_dict = {category: "" for category in self.categories}
        self.article_count = 10

    def get_top_headlines_for_categories(self):
        for category in self.categories:
            response = requests.get(f'https://newsdata.io/api/1/news?apikey={news_api_key}&q'
                                    f'={category}&country=us&language=en').json()
            self.categories_dict[category] = summarize_article(response["results"][0]["content"])

    def get_summarized_news(self):
        self.get_top_headlines_for_categories()
        return self.categories_dict


def summarize_article(content):
    prompt = f"""Summarize this paragraph and detail some relevant context.

        Text: "In response to a new report warning of irreversible damage from climate change, global efforts to 
        combat the crisis have intensified. The report, released by an international team of scientists, 
        highlights the urgency of addressing climate change and its potential consequences on a planetary scale. 
        he report outlines various key findings, including:

        Rising Sea Levels: The report indicates that without immediate action, sea levels could rise by over two 
        meters by the end of the century, leading to significant coastal inundation and displacing millions of 
        people.

        Extreme Weather Events: Climate change is contributing to more frequent and intense extreme weather 
        events, such as hurricanes, droughts, and heatwaves, posing a serious threat to human lives, 
        infrastructure, and agriculture.
        
        Biodiversity Loss: The loss of biodiversity is accelerating due to climate change, with many species facing 
        extinction if decisive action is not taken.
        
        Global Food Security: Changing weather patterns and reduced agricultural productivity may result in food 
        shortages, impacting vulnerable populations around the world.
        
        In response to the report's findings, policymakers and activists are calling for urgent and ambitious 
        action to reduce greenhouse gas emissions, transition to renewable energy sources, and implement 
        adaptation measures to protect communities from the impacts of climate change.
        
        Many countries have pledged to enhance their commitments under the Paris Agreement, while businesses are 
        being urged to adopt sustainable practices. Additionally, public awareness campaigns are being launched 
        to educate people about the importance of individual actions in mitigating climate change.
        
        The report serves as a stark reminder of the critical need for immediate and collaborative efforts to 
        address climate change and safeguard the planet for future generations."
        
        Summary: An international team of scientists releases a report warning of irreversible climate change 
        consequences. Sea levels could rise by over two meters, extreme weather events are becoming more 
        frequent, biodiversity loss is accelerating, and global food security is at risk. Policymakers and 
        activists call for urgent action to reduce emissions and transition to renewable energy. Countries pledge 
        to enhance commitments under the Paris Agreement, businesses urged to adopt sustainable practices, 
        and public awareness campaigns launched. The report emphasizes the need for collaborative efforts to 
        protect the planet.

        Text: {content}
        
        Summary:"""
    response = palm.generate_text(
        **defaults,
        prompt=prompt
    )
    return response.result
