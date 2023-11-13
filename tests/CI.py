import unittest
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from twitter_user_tweet_crawler.tweet import Tweet


def get_browser() -> WebDriver:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--disable-remote-fonts')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


class TestCase(unittest.TestCase):
    def test_spider(self):
        browser = get_browser()
        browser.get('https://twitter.com/_CASTSTATION/status/1697029186777706544')
        sleep(20)
        element = browser.find_element(By.XPATH,"//*[contains(text(), '{}')]".format('miku miku oo ee oo'))
        browser.save_screenshot('debug.png')
        self.assertIn('miku miku oo ee oo',element.get_attribute('innerHTML'))


if __name__ == '__main__':
    unittest.main()
