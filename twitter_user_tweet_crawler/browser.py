from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver



def get_browser(headless: bool = False) -> WebDriver:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--disable-remote-fonts')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1200x600')
    if headless:
        chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.__dict__['is_using'] = False
    return driver


def get_multiple_browsers(count: int, headless: bool = False) -> list[WebDriver]:
    return [get_browser(headless) for _ in range(count)]
