import concurrent.futures
import re
from datetime import datetime
from pathlib import Path
from time import sleep
from urllib.parse import quote, urlparse

from html2text import html2text
from loguru import logger
from requests import get
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from .util.config import config
from .util.sql import insert_new_record, is_id_exists

inject: str
inject_js = config.inject_js
with open(config.inject_js, 'r') as fp:
    inject = fp.read()


class CrawlError(Exception):
    pass


def catch(func):
    def wrapper(self, available_driver: WebDriver):
        try:
            return func(self, available_driver)
        except:
            logger.error(available_driver.current_url)

    return wrapper


class Tweet:
    post_id: int
    post_time: int
    img: list[str] | None
    video: str | None
    text: str
    via_app: str | None
    location: str | None
    link: str
    driver: WebDriver

    def __init__(self, link: str):
        self.post_time = 0
        self.post_id = int(urlparse(link).path.split('/')[-1])
        self.link = link
        self.text = ''
        self.video = None
        self.img = None
        self.via_app = None
        self.location = None

    @logger.catch
    def download_res(self, url: str, path: str):
        if not (Path(config.save) / 'res' / path).exists():
            with open(Path(config.save) / 'res' / path, 'wb') as fp:
                fp.write(get(url, proxies=config.proxy, headers=config.header).content)

    @logger.catch
    def write_markdown(self):
        if not (Path(config.save) / f'{self.post_id}.md').exists():
            with open(Path(config.save) / f'{self.post_id}.md', 'w') as f:
                f.write(self.text)

    @logger.catch
    def commit_sqlite(self):
        if not is_id_exists(int(self.post_id)):
            insert_new_record(self.post_id, self.post_time, self.location)

    @catch
    def load_data(self, available_driver: WebDriver):
        self.driver = available_driver

        def replace_emoji(string: str) -> str:
            if re.search(r'\!\[(.*?)\]\(https://.*\.twimg\.com/emoji/(.*?)\.svg\)', string, re.MULTILINE):
                return re.sub(r'\!\[(.*?)\]\(https://.*\.twimg\.com/emoji/(.*?)\.svg\)', r'\1', string, re.MULTILINE)
            return string

        def get_video(base_dom: WebElement):
            if not base_dom.find_element(By.XPATH, "//video").is_displayed():
                raise CrawlError("Can't crawl videos")
            elemet: WebElement = base_dom.find_element(By.XPATH, "//div[contains(@class, \"tmd-down\")]")
            sleep(1)
            ActionChains(available_driver).move_to_element(elemet).click().perform()
            count: int = 0
            while available_driver.execute_script("return document.isParsed;") is False:
                if (count := count + 1) > 10:
                    raise CrawlError("Timeout Error")
                sleep(1)
                ActionChains(available_driver).move_to_element(elemet).click().perform()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(self.download_res, available_driver.execute_script("return document.fileList;"),
                             available_driver.execute_script("return document.fileName;"))
            return list(set(available_driver.execute_script("return document.fileName;")))[0]

        def get_img(base_dom):
            result = base_dom.find_elements(By.XPATH, '//img')
            for i in result:
                if 'card_img' in i.get_attribute('src'):
                    raise CrawlError("Can't crawl pictures")
            elemet: WebElement = base_dom.find_element(By.XPATH, "//div[contains(@class, \"tmd-down\")]")
            sleep(1)
            ActionChains(available_driver).move_to_element(elemet).click().perform()
            count: int = 0
            while available_driver.execute_script("return document.isParsed;") is False:
                if (count := count + 1) > 10:
                    raise CrawlError("Timeout Error")
                ActionChains(available_driver).move_to_element(elemet).click().perform()
                sleep(1)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(self.download_res, available_driver.execute_script("return document.fileList;"),
                             available_driver.execute_script("return document.fileName;"))
            return list(set(available_driver.execute_script("return document.fileName;")))

        def click_sensitive_element():
            try:
                items = available_driver.find_elements(By.XPATH, "//span[text()='View']")
                for i in items:
                    ActionChains(available_driver).move_to_element(i).click(i).perform()
            except:
                pass
            sleep(0.5)

        def get_time(base_dom):
            time_stamp = base_dom.find_element(By.XPATH, '//time').get_attribute('datetime')
            return int(datetime.fromisoformat(time_stamp.replace('Z', '+00:00')).timestamp())

        def get_location(base_dom):
            result = base_dom.find_element(By.XPATH, '//a[contains(@href, \'place\')]')
            return result.text + '(' + result.get_attribute('href') + ')'

        def get_via_app(base_dom):
            result: WebElement = base_dom.find_element(By.XPATH, '//*[@data-testid=\'card.wrapper\']//*['
                                                                 '@data-testid=\'card.layoutSmall.media\']')
            return html2text(result.get_attribute('innerHTML')).replace('\n\n', '\n')

        def wait_element(count: int = 0):
            try:
                wait = WebDriverWait(available_driver, 30)
                wait.until(EC.presence_of_element_located((By.XPATH, "//article[@data-testid=\"tweet\"]//time")))
            except TimeoutException:
                if count > 3:
                    raise CrawlError("Waiting time is too long, timeout")
                sleep(20)
                available_driver.refresh()
                wait_element(count + 1)

        available_driver.get(self.link)
        available_driver.execute_script(inject)
        wait_element()
        dom = available_driver.find_element(By.XPATH, f"//a[contains(@href, '{self.post_id}')]/ancestor::*[6]"
                                                      f"[descendant::time]")
        click_sensitive_element()
        self.post_time = get_time(dom)
        try:
            self.video = get_video(dom)
        except:
            self.video = None
        try:
            self.img = get_img(dom)
        except:
            self.img = None
        try:
            self.location = get_location(dom)
        except:
            self.location = None
        try:
            self.via_app = get_via_app(dom)
        except:
            self.via_app = None
        try:
            self.text = replace_emoji(html2text(
                dom.find_element(By.XPATH, '//*[@data-testid="tweetText"]').get_attribute('innerHTML'))).strip()
        except:
            self.text = ''
        if self.img:
            for i in self.img:
                self.text += f'\n![]({config.save}/res/{quote(str(i))})\n'
        if self.video:
            self.text += f'<video src="{config.save}/res/{quote(str(self.video))}"></video>\n'
        if self.location:
            self.text += '\nLocation:' + self.location + '\n'
        if self.via_app:
            self.text += self.via_app
        self.print()
        self.write_markdown()
        self.commit_sqlite()

    def print(self):
        console = Console()
        table = Table(title='Summary')
        header = "post_id", "post_time", "img", "video", "text", "via_app", "location", "link"
        row = (str(self.post_id), str(self.post_time), ', '.join(self.img) if self.img else ''
               , self.video, Markdown(self.text), self.via_app, self.location, self.link)
        for i in header:
            table.add_column(i)
        table.add_row(*row)
        console.print(table)
