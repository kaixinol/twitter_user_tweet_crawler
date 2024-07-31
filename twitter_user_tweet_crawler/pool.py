from concurrent.futures import ThreadPoolExecutor, Future
from time import sleep
from typing import Callable

from rich.prompt import Confirm
from selenium.webdriver.chrome.webdriver import WebDriver

from twitter_user_tweet_crawler.util.lock import mutex, get, update

slow_mode = Confirm.ask("Do you want to enable slow mode?", default=False)


class ThreadPool:
    browser: list[WebDriver]
    jobs: list[Callable] = []
    pool: ThreadPoolExecutor

    def __init__(self, browser: list[WebDriver], pool: ThreadPoolExecutor):
        self.browser = browser
        self.pool = pool

    def check_and_work(self):
        if not self.jobs:
            return
        for i in self.browser:
            with mutex:
                if not get()[id(i)]:
                    i: WebDriver
                    update({id(i): True})
                    job = self.jobs.pop(0)
                    callback: Future = self.pool.submit(job, i)
                    callback.add_done_callback(lambda future: self._on_job_complete(i, callback))
                    return

    def _on_job_complete(self, index, future):
        elements = self.browser.index(index)
        try:
            future.result()
        # By default, `concurrent.futures` will silently log errors but will not raise them
        # Throw the error directly
        finally:
            if slow_mode:
                sleep(10)
            with mutex:
                update({id(self.browser[elements]): False})

            self.check_and_work()
