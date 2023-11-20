import unittest
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from twitter_user_tweet_crawler.browser import get_browser
from twitter_user_tweet_crawler.util.config import config

config.load({"proxy": None, "max_threads": 2,
             "header": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                      "like Gecko) "}
                , "inject_js": "script.js",
             }
            )


class TestCase(unittest.TestCase):
    def test_spider(self):
        browser = get_browser(headless=True)
        browser.get('https://twitter.com/_CASTSTATION/status/1697029186777706544')
        sleep(20)
        element = browser.find_element(By.XPATH, "//*[contains(text(), '{}')]".format('miku miku oo ee oo'))
        browser.save_screenshot('debug.png')
        self.assertIn('miku miku oo ee oo', element.get_attribute('innerHTML'))


if __name__ == '__main__':
    unittest.main()
