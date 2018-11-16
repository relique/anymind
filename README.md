# Tweet Scraper

The script uses Flask as a RESTful API backend and Selenium in order to scrape tweets from Twitter.
Flask will open a local web server on port 5000.
Selenium will spin a browser in a separate window, so don't worry about that, just let it finish.

## Installation

1. Make sure you're on a computer with either macOS or Linux installed. Windows isn't supported.

2. Make sure you have Python 3.6 or newer.

3. Install the latest Google Chrome browser.

4. Install requirements:
```bash
pip install -r requirements.txt
```

5. `cd` to the root script folder and run:
```bash
python api.py
```

## How to use

### Get tweets by a hashtag

Returns the list of tweets with the given hashtag. Optional parameters:
* *limit:* integer, specifies the number of tweets to retrieve, default is 30

Sample requests:
* http://127.0.0.1:5000/hashtags/Django
* http://127.0.0.1:5000/hashtags/Python?limit=40

### Get user tweets

Returns the list of tweets that user has on her feed. Optional parameters:
* *limit:* integer, specifies the number of tweets to retrieve, default is 30

Sample requests:
* http://127.0.0.1:5000/users/agvsmontero
* http://127.0.0.1:5000/users/kianathehackr?limit=10

## Tests

`cd` to the root script folder and run:
```bash
python test.py
```
