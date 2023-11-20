import concurrent.futures
import json
from pathlib import Path
from time import sleep
from urllib.parse import urlparse

from loguru import logger
from rich.prompt import Confirm
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from .browser import get_browser, get_multiple_browsers
from .pool import ThreadPool
from .util.config import config, work_directory, set_work_directory


def main():
    from .tweet import Tweet
    cookie: list[dict]
    work_list: list[WebDriver]
    driver: WebDriver

    def read_config() -> list[dict]:
        with open(work_directory / 'cookie.json', 'r') as f:
            return json.load(f)

    def write_config(data: list[dict]):
        with open(work_directory / 'cookie.json', 'w') as f:
            json.dump(data, f)

    def set_cookie(browser: WebDriver):
        for i in cookie:
            browser.add_cookie(i)

    def get_executor(count: int | None = None):
        return concurrent.futures.ThreadPoolExecutor(max_workers=count)

    def get_items_need_handle():
        return driver.find_elements(*selector)

    selector = (By.XPATH, '//*/div[2]/div/div[3]/a[@role="link"]')
    (Path(config.save) / 'res').mkdir(exist_ok=True, parents=True)

    driver = get_browser()

    tweet_executor = get_executor(config['max_threads'])
    work_list = get_multiple_browsers(config['max_threads'], headless=True)
    wait_list = []
    for i in work_list:
        wait_list.append(tweet_executor.submit(i.get, 'https://twitter.com/404'))
    for ii in wait_list:
        ii.result()
    driver.get('https://twitter.com/404')
    if not Path(work_directory / 'cookie.json').exists():
        input("Cookie cache was not found. Please press Enter after logging in.")
        write_config(driver.get_cookies())
    else:
        use_cache = Confirm().ask("Cookie cache detected, do you want to use it?", default=True)
        if not use_cache:
            input("Please press Enter after logging in")
            write_config(driver.get_cookies())
        else:
            cookie = read_config()
            set_cookie(driver)
    cookie = driver.get_cookies()
    for drivers in work_list:
        set_cookie(drivers)
    driver.get("https://twitter.com/" + config.user)
    data_dict = {}
    pool = ThreadPool(work_list, tweet_executor)

    while True:
        # Looping drop-down scroll bar
        driver.execute_script("window.scrollBy(0, 200)")
        sleep(1)
        try:
            links = get_items_need_handle()
            for i in links:
                full_url = i.get_attribute("href")
                tweet_id = urlparse(full_url).path.split('/')[-1]
                if tweet_id not in data_dict:
                    data_dict[tweet_id] = Tweet(full_url)
                    pool.jobs.append(data_dict[tweet_id].load_data)
                    logger.info(full_url)
            pool.check_and_work()
        except:
            pass


if __name__ == "__main__":
    set_work_directory(Path(__file__).absolute().parent)
    logger.add(work_directory / "log/{time:YYYY-MM-DD}.log", rotation="00:00",
               level="ERROR",
               encoding="utf-8", format="{time} | {level} | {message}", enqueue=True)
    Path(Path(__file__).absolute().parent / 'output/res').mkdir(parents=True, exist_ok=True)
    config.load("config.yaml")
    main()
