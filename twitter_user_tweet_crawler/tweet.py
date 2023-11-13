import re
from datetime import datetime

from emoji import is_emoji
from html2text import html2text
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from .__main__ import *
from .util.config import work_directory
from .util.sql import insert_new_record


class Tweet:
    post_id: int
    post_time: int
    img: list[str] | None
    video: str | None
    text: str
    via_app: str | None
    location: str | None
    link: str

    def __init__(self, link: str):
        self.post_time = int(datetime.now().timestamp())
        self.post_id = int(urlparse(link).path.split('/')[-1])
        self.link = link
        self.text = ''
        self.video = None
        self.img = None
        self.via_app = None
        self.location = None

    @logger.catch
    def write_markdown(self):
        if not Path(work_directory / 'output' / f'{self.post_id}.md').exists():
            with open(work_directory / 'output' / f'{self.post_id}.md', 'w') as f:
                f.write(self.text)

    @logger.catch
    def commit_sqlite(self):
        insert_new_record(self.post_id, self.post_time, self.location)

    def load_data(self, available_driver: WebDriver):

        def replace_emoji(string: str) -> str:
            if re.search(r'\!\[(.*?)\]\(https://.*\.twimg\.com/emoji/(.*?)\.svg\)', string, re.MULTILINE):
                return re.sub(r'\!\[(.*?)\]\(https://.*\.twimg\.com/emoji/(.*?)\.svg\)', r'\1', string, re.MULTILINE)
            return string

        def get_video():
            try:
                elemet = available_driver.find_element(By.XPATH, "//div[contains(@class, \"tmd-down\")]")
            except:
                return
            sleep(3)
            ActionChains(available_driver).move_to_element(elemet).click().perform()
            available_driver.execute_script("document.isDownloaded = false;document.fileList=[];")
            while not available_driver.execute_script("return document.isDownloaded===true;"):
                sleep(1)
            self.video = list(available_driver.execute_script("return document.fileList"))[0]

        def get_img():
            try:
                elemet = available_driver.find_element(By.XPATH, "//div[contains(@class, \"tmd-down\")]")
            except:
                return
            sleep(3)
            ActionChains(available_driver).move_to_element(elemet).click().perform()
            available_driver.execute_script("document.isDownloaded = false;document.fileList=[];")
            while not available_driver.execute_script("return document.isDownloaded===true;"):
                sleep(1)
            self.img = list(available_driver.execute_script("return document.fileList"))

        def click_sensitive_element():
            try:
                items = available_driver.find_elements(By.XPATH, "//span[text()='查看']")
                for i in items:
                    ActionChains(available_driver).move_to_element(i).click().perform()
            except:
                pass
            sleep(0.5)

        result = None
        available_driver.get(self.link)
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
                self.text += f'\n![](./res/{quote(i)})\n'
        if video:
            self.text += f'<video src="./res/{quote(str(self.video))}"></video>\n'
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
