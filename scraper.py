import os
import platform
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Tweet(object):
    """Single tweet representation class."""
    def __init__(self, elem):
        self.elem = elem

    def _get_badge_count(self, subclass):
        elem = self.elem.find_element_by_css_selector(
            f'.ProfileTweet-action--{subclass} .ProfileTweet-actionCountForPresentation')
        return elem.text

    def _get_account_data(self):
        """Return a dict containing user metadata."""
        account_tag = self.elem.find_element_by_class_name('account-group')
        return {
            'fullname': self.elem.find_element_by_class_name('fullname').text,
            'href': f'/{account_tag.get_attribute("href").split("/")[-1]}',
            'id': account_tag.get_attribute('data-user-id')
        }

    def _get_date(self):
        """Return a tweet's timestamp."""
        tag = self.elem.find_element_by_class_name('tweet-timestamp')
        return tag.get_attribute('title')

    @property
    def hashtags(self):
        """Return a hashtag generator."""
        for elem in self.elem.find_elements_by_class_name('twitter-hashtag'):
            yield elem.text

    @property
    def likes(self):
        """Return total likes."""
        return self._get_badge_count('favorite')

    @property
    def retweets(self):
        """Return total retweets."""
        return self._get_badge_count('retweet')

    @property
    def replies(self):
        """Return total replies."""
        return self._get_badge_count('reply')

    @property
    def text(self):
        """Return a tweet message."""
        return self.elem.find_element_by_class_name('tweet-text').text

    def to_representation(self):
        """Convert a tweet into an API-friendly representation."""
        data = {
            'account': self._get_account_data(),
            'date': self._get_date(),
            'hashtags': list(self.hashtags),
            'likes': self.likes,
            'replies': self.replies,
            'retweets': self.retweets,
            'text': self.text
        }
        return data


class _TweetScraper(object):
    """Base class for creating tweet scrapers."""
    def __init__(self, query, limit):
        self.query = query
        self.limit = limit
        self.driver = webdriver.Chrome(executable_path=self.get_driver_path())

    def _scroll_down(self):
        """Scroll to the bottom of the page."""
        self.driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(3)

    def _get_tweets(self):
        """Return a list of tweets."""
        def find_all():
            return self.driver.find_elements_by_class_name('tweet')

        self.driver.get(self.url)
        time.sleep(5)
        retries = 0
        while len(find_all()) < self.limit:
            last_total = len(find_all())
            self._scroll_down()
            if len(find_all()) == last_total:
                retries += 1
                if retries == 3:  # end of timeline
                    break
        return find_all()[:self.limit]

    @property
    def url(self):
        """Build a Twitter URL to scrape from."""
        base_url = 'https://twitter.com/search'
        if self.query_type == 'hashtag':
            return f'{base_url}?q=%23{self.query}'
        else:
            return f'{base_url}?q=from%3A{self.query}'

    def scrape(self):
        """Return tweets that are ready for API use."""
        result = []
        for elem in self._get_tweets():
            result.append(Tweet(elem).to_representation())
        self.driver.quit()
        return result

    @staticmethod
    def get_driver_path():
        """Build an absolute path to a Chrome Driver.
        Additionally check whether the OS is compatible or not.
        """
        osname = platform.system().lower()
        if osname == 'linux':
            filename = 'chromedriver_linux'
        elif osname == 'darwin':
            filename = 'chromedriver_mac'
        else:
            raise Exception('You can only run it on either macOS or Linux.')
        return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            'webdrivers', filename)


class TweetsByHashtagScraper(_TweetScraper):
    """Tweet scraper that filters by a hashtag."""
    query_type = 'hashtag'


class TweetsByUserScraper(_TweetScraper):
    """Tweet scraper that filters by a user."""
    query_type = 'user'
