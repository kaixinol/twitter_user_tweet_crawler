import concurrent.futures
import re
from datetime import datetime
from pathlib import Path
from time import sleep
from urllib.parse import quote, urlparse

from emoji import is_emoji
from html2text import html2text
from loguru import logger
from requests import get
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .util.config import config
from .util.sql import insert_new_record, is_id_exists

inject: str
inject_js = config.inject_js
with open(config.inject_js, 'r') as fp:
    inject = fp.read()


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
        with open(Path(config.save) / 'res' / path, 'wb') as fp:
            fp.write(get(url, proxies=config.proxy, headers=config.header).content)

    @logger.catch
    def write_markdown(self):
        if not (Path(config.save) / f'{self.post_id}.md').exists():
            with open(Path(config.save) / f'{self.post_id}.md', 'w') as f:
                f.write(self.text)

    @logger.catch()
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

        def get_video():
            try:
                elemet = available_driver.find_element(By.XPATH, "//div[contains(@class, \"tmd-down\")]")
            except:
                return
            sleep(1)
            ActionChains(available_driver).move_to_element(elemet).click().perform()
            while available_driver.execute_script("return document.isParsed;") is False:
                sleep(0.5)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(self.download_res, available_driver.execute_script("return document.fileList;"),
                             available_driver.execute_script("return document.fileName;"))
            self.video = available_driver.execute_script("return document.fileName;")[0]

        def get_img():
            try:
                elemet = available_driver.find_element(By.XPATH, "//div[contains(@class, \"tmd-down\")]")
            except:
                return
            sleep(1)
            ActionChains(available_driver).move_to_element(elemet).click().perform()
            while available_driver.execute_script("return document.isParsed;") is False:
                sleep(0.5)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(self.download_res, available_driver.execute_script("return document.fileList;"),
                             available_driver.execute_script("return document.fileName;"))
            self.img = available_driver.execute_script("return document.fileName;")

        def click_sensitive_element():
            try:
                items = available_driver.find_elements(By.XPATH, "//span[text()='View']")
                for i in items:
                    ActionChains(available_driver).move_to_element(i).click().perform()
            except:
                pass
            sleep(0.5)

        result = None
        available_driver.get(self.link)
        available_driver.execute_script(inject)
        wait = WebDriverWait(available_driver, 20)
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//*/time/ancestor::*[3]')))
        time_stamp = element.find_element(By.XPATH, '//time').get_attribute('datetime')
        location = True
        try:
            result = element.find_element(By.XPATH, '//a[contains(@href, \'place\')]')
        except:
            location = False
        if location:
            self.location = result.text + '(' + result.get_attribute('href') + ')'
        # 移除多余元素，不这样写的话用其他方式写会卡住，我不想深究了TAT
        available_driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", element)
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div['
                                                                       '2]/main//section/div/div/div['
                                                                       '1]/div/div/article/div/div/div['
                                                                       '3]//div[@role=\'group\' and @aria-label]')))
        video = True
        try:
            result = available_driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div['
                                                             '2]/main//section/div/div/div['
                                                             '1]/div/div/article/div/div/div[3]//video')
        except:
            video = False
        if video:
            get_video()
        click_sensitive_element()
        img = True
        try:
            result = available_driver.find_elements(By.XPATH, '//*[@id="react-root"]/div/div/div['
                                                              '2]/main//section/div/div/div['
                                                              '1]/div/div/article/div/div/div[3]//img')
        except:
            img = False
        for i in result:
            if (img and 'card_img' not in i.get_attribute('src')
                    and not is_emoji(i.get_attribute('alt'))
                    and 'profile_images' not in i.get_attribute('src')):
                get_img()
                break
        available_driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", element)
        element = available_driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]'
                                                          '/main//section/div/div/div[1]/div/'
                                                          'div/article/div/div/div[3]')
        self.post_time = int(datetime.fromisoformat(time_stamp.replace('Z', '+00:00')).timestamp())
        text = True
        try:
            result = element.find_element(By.XPATH, '//*[@data-testid="tweetText"]').get_attribute('innerHTML')
        except:
            text = False
        if text:
            self.text = replace_emoji(html2text(result)).strip()
        via_app = True
        try:
            result = element.find_element(By.XPATH, '//*[@data-testid=\'card.wrapper\']//*['
                                                    '@data-testid=\'card.layoutSmall.media\']')
            is_visible = available_driver.execute_script("return arguments[0].offsetParent !== null;", result)
            if not is_visible:
                raise
        except:
            via_app = False
        if via_app:
            self.via_app = html2text(result.get_attribute('innerHTML')).replace('\n\n', '\n')
        if self.img:
            for i in self.img:
                self.text += f'\n![]({config.save}/res/{quote(str(i))})\n'
        if video:
            self.text += f'<video src="{config.save}/res/{quote(str(self.video))}"></video>\n'
        if self.location:
            self.text += 'Location:' + self.location + '\n'
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
