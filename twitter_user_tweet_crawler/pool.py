from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable

from loguru import logger
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver


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
            if not i.__dict__['is_using']:
                i: WebDriver
                i.__dict__['is_using'] = True
                job = self.jobs.pop()
                callback: Future = self.pool.submit(job, i)
                callback.add_done_callback(lambda future: self._on_job_complete(i, callback))
                return

    @logger.catch
    def _on_job_complete(self, index, future):
        elements = self.browser.index(index)
        try:
            future.result()
        # By default, `concurrent.futures` will silently log errors but will not raise them
        # Throw the error directly
        except NoSuchElementException:
            pass
        finally:
            self.browser[elements].__dict__['is_using'] = False
            self.check_and_work()
