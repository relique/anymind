from flask import Flask
from flask_restful import Resource, Api, reqparse
from scraper import TweetsByHashtagScraper, TweetsByUserScraper

DEFAULT_LIMIT = 30

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, help='Limit number of tweets')


class TweetsByHashtag(Resource):
    """Endpoint for tweets filtered by a hashtag."""
    def get(self, hashtag):
        args = parser.parse_args()
        limit = args['limit'] or DEFAULT_LIMIT
        return TweetsByHashtagScraper(hashtag, limit).scrape()


class TweetsByUser(Resource):
    """Endpoint for tweets filtered by a user."""
    def get(self, username):
        args = parser.parse_args()
        limit = args['limit'] or DEFAULT_LIMIT
        return TweetsByUserScraper(username, limit).scrape()


api.add_resource(TweetsByHashtag, '/hashtags/<string:hashtag>')
api.add_resource(TweetsByUser, '/users/<string:username>')


if __name__ == '__main__':
    app.run(debug=True)
