import json
from pathlib import Path
from time import sleep

from twitter_user_tweet_crawler.browser import get_browser
from twitter_user_tweet_crawler.util.config import set_work_directory, config, work_directory


def get_tweet():
    set_work_directory(Path(__file__).absolute().parent)
    config.load({"proxy": {"http": "socks5://127.0.0.1:7890", "https": "socks5://127.0.0.1:7890"}, "max_threads": 2,
                 "header": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                          "like Gecko) "}, "inject_js": "/media/Data/Project"
                                                                        "/twitter_user_tweet_crawler/script.js",

                 "save": "/media/Data/Project/twitter_user_tweet_crawler/output/",
                 "user": "plantgazer"})

    from twitter_user_tweet_crawler.tweet import Tweet
    (Path(config.save) / 'res').mkdir(parents=True, exist_ok=True)
    browser = get_browser(headless=True)
    browser.get('https://twitter.com/404')
    cookie: list[dict]
    input("After logging in, press Enter")
    if (work_directory / 'cookie.json').exists():
        with open(work_directory / 'cookie.json', 'r') as f:
            cookie = json.load(f)
        for i in cookie:
            browser.add_cookie(i)
    Tweet('https://twitter.com/plantgazer/status/692426044368908289').load_data(browser)
    sleep(10000)


get_tweet()
