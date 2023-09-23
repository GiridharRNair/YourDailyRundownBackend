import feedparser

# RSS feed URL
RSS_URL = "https://theathletic.com/feeds/rss/news/"


class TheAthleticParser:
    """
    A class for parsing sports articles from The Athletics' RSS feed.
    """

    def __init__(self):
        """
        Initialize the TheAthleticParser instance with an empty list to store article information.
        """
        self.article_list = []

    def get_articles(self):
        """
        Retrieve and aggregate information for all sports articles from the RSS feed.

        :return: A list containing dictionaries with information about each article.
        :rtype: list[dict]
        """
        feed = feedparser.parse(RSS_URL)
        for entry in feed.entries:
            url = entry.link
            title = entry.title
            image_list = []

            for link in entry.links:
                if 'rel' in link and link['rel'] == 'enclosure':
                    image_url = link['href']
                    image_list.append({"url": image_url})

            self.article_list.append({"url": url,
                                      "title": title,
                                      "multimedia": image_list})

        return self.article_list
