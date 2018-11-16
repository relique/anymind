import json
import types
import unittest
import flask

from unittest.mock import Mock, patch
from scraper import Tweet, _TweetScraper
from api import app, DEFAULT_LIMIT


class TweetTestCase(unittest.TestCase):
    def setUp(self):
        self.tweet = Tweet(Mock())
        self.full_name = 'John Doe'
        self.user_id = '226405509'
        self.date = '7:00 AM - 17 Sep 2018'

    def test__get_badge_count(self):
        mock_elem = Mock()
        mock_elem.find_element_by_css_selector().text = 15
        self.assertEqual(Tweet(mock_elem)._get_badge_count('favorite'), 15)

    def test__get_account_data(self):
        mock_elem = Mock()
        mock_elem.find_element_by_class_name().text = self.full_name
        mock_elem.find_element_by_class_name().get_attribute().split.return_value = \
            'https://twitter.com/johndoe'.split('/')
        data = Tweet(mock_elem)._get_account_data()
        self.assertEqual(data['fullname'], self.full_name)
        self.assertEqual(data['href'], '/johndoe')
        mock_elem.find_element_by_class_name().get_attribute.return_value = self.user_id
        data = Tweet(mock_elem)._get_account_data()
        self.assertEqual(data['id'], self.user_id)

    def test__get_date(self):
        mock_elem = Mock()
        mock_elem.find_element_by_class_name().get_attribute.return_value = self.date
        self.assertEqual(Tweet(mock_elem)._get_date(), self.date)

    def test_hashtags(self):
        self.assertTrue(isinstance(self.tweet.hashtags, types.GeneratorType))

    @patch('scraper.Tweet._get_badge_count', return_value=10, autospec=True)
    def test_likes(self, mock__get_badge_count):
        self.assertEqual(self.tweet.likes, 10)
        mock__get_badge_count.assert_called_once_with(self.tweet, 'favorite')

    @patch('scraper.Tweet._get_badge_count', return_value=20, autospec=True)
    def test_retweets(self, mock__get_badge_count):
        self.assertEqual(self.tweet.retweets, 20)
        mock__get_badge_count.assert_called_once_with(self.tweet, 'retweet')

    @patch('scraper.Tweet._get_badge_count', return_value=20, autospec=True)
    def test_replies(self, mock__get_badge_count):
        self.assertEqual(self.tweet.replies, 20)
        mock__get_badge_count.assert_called_once_with(self.tweet, 'reply')

    def test_text(self):
        mock_elem = Mock()
        mock_elem.find_element_by_class_name().text = 'message'
        self.assertEqual(Tweet(mock_elem).text, 'message')

    @patch('scraper.Tweet.hashtags', autospec=True)
    @patch('scraper.Tweet._get_date', autospec=True)
    @patch('scraper.Tweet._get_account_data', autospec=True)
    def test_to_representation(self, mock__get_account_data, mock__get_date,
                               mock_hashtags):
        account_data = {
            'fullname': self.full_name,
            'href': '/johndoe',
            'id': self.user_id
        }
        mock__get_account_data.return_value = account_data
        mock__get_date.return_value = self.date
        data = self.tweet.to_representation()
        self.assertEqual(data['account'], account_data)
        self.assertEqual(data['date'], self.date)
        self.assertIn('hashtags', data)
        self.assertIn('likes', data)
        self.assertIn('retweets', data)
        self.assertIn('replies', data)
        self.assertIn('text', data)
        mock__get_account_data.assert_called_once()
        mock__get_date.assert_called_once()


class _TweetScraperTestCase(unittest.TestCase):
    @patch('scraper.webdriver.Chrome', autospec=True)
    def setUp(self, mock_chrome):
        self.scraper = _TweetScraper('Python', 10)

    @patch('scraper.platform.system', autospec=True)
    def test_get_driver_path(self, mock_system):
        mock_system.return_value = 'Linux'
        self.assertTrue(self.scraper.get_driver_path().endswith('chromedriver_linux'))
        mock_system.return_value = 'Darwin'
        self.assertTrue(self.scraper.get_driver_path().endswith('chromedriver_mac'))
        mock_system.return_value = 'Windows'
        with self.assertRaises(Exception):
            self.scraper.get_driver_path()

    def test_url(self):
        self.assertEqual(self.scraper.url, 'https://twitter.com/search?q=%23Python')
        self.scraper.query_type = 'user'
        self.assertEqual(self.scraper.url, 'https://twitter.com/search?q=from%3APython')

    @patch('scraper.time.sleep')
    @patch('scraper._TweetScraper._scroll_down', autospec=True)
    def test__get_tweets(self, mock__scroll_down, mock_sleep):
        tweets = [1, 2, 3, 4]
        mock_driver = Mock()
        mock_driver.find_elements_by_class_name.return_value = tweets
        self.scraper.driver = mock_driver
        self.assertEqual(self.scraper._get_tweets(), tweets)
        self.scraper.limit = 2
        self.assertEqual(self.scraper._get_tweets(), tweets[:2])

    @patch('scraper.time.sleep')
    @patch('scraper.Tweet.to_representation', return_value={}, autospec=True)
    @patch('scraper._TweetScraper._get_tweets', return_value=[1, 2, 3],
           autospec=True)
    def test_scrape(self, mock__get_tweets, mock_to_repr, mock_sleep):
        self.assertEqual(len(self.scraper.scrape()), 3)


class TweetsByHashtagTestCase(unittest.TestCase):
    def test_request(self):
        with app.test_request_context('/hashtags/Python'):
            self.assertEqual(flask.request.path, '/hashtags/Python')
            self.assertNotIn('limit', flask.request.args)
        with app.test_request_context('/hashtags/Python?limit=20'):
            self.assertEqual(flask.request.path, '/hashtags/Python')
            self.assertEqual(int(flask.request.args['limit']), 20)

    def test_response(self):
        with app.test_client() as client:
            response = client.get('/hashtags/Python')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(json.loads(response.data)), DEFAULT_LIMIT)
            response = client.get('/hashtags/Python?limit=5')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(json.loads(response.data)), 5)


class TweetsByUserTestCase(unittest.TestCase):
    def test_request(self):
        with app.test_request_context('/users/stevewoz'):
            self.assertEqual(flask.request.path, '/users/stevewoz')
            self.assertNotIn('limit', flask.request.args)
        with app.test_request_context('/users/stevewoz?limit=20'):
            self.assertEqual(flask.request.path, '/users/stevewoz')
            self.assertEqual(int(flask.request.args['limit']), 20)

    def test_response(self):
        with app.test_client() as client:
            response = client.get('/users/stevewoz')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(json.loads(response.data)), DEFAULT_LIMIT)
            response = client.get('/users/stevewoz?limit=5')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(json.loads(response.data)), 5)


if __name__ == '__main__':
    unittest.main()
