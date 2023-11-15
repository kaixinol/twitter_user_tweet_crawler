> [!NOTE]  
> 注意：下载推文中的音频该功能暂未支持。

> [!WARNING]
> 不要泄漏自己的`cookie.json`，这将导致你的推特账号被盗。

![](https://github.com/kaixinol/twitter_user_tweet_crawler/actions/workflows/python-app.yaml/badge.svg)

## 简介
- 此工具能够自动的模拟浏览器操作爬取用户的全部推文并将全部静态资源(视频、图片)保存在本地,无需调用Twitter API
- 同时利用sqlite3将爬取到的数据保存为索引文件，方便查询。
## 安装
### 安装依赖
- 安装`Python3.10+`
- 安装`Poetry`
- 安装`Chrome 119.0+`
- 在有`pyproject.toml`的目录运行指令`poetry install`
### 准备配置
- 配置`config.yaml`
- 编辑`/twitter_user_tweet_crawler/__main__.py`的69行
- 准备Chrome用户数据文件夹 <i><u>（将data_dir设置为`/twitter_user_tweet_crawler/userdata/`为例）</u></i>
  1. 在`/twitter_user_tweet_crawler/userdata/`下新建文件夹
  2. 你需要同时进行***n个浏览器实例***就新建***n+1个文件夹***
  3. 比方说你需要3个线程同时工作
  4. 就新建`/twitter_user_tweet_crawler/userdata/1` `/twitter_user_tweet_crawler/userdata/2` `/twitter_user_tweet_crawler/userdata/3`  `/twitter_user_tweet_crawler/userdata/4` 
- 预配置 Chrome
  1. 执行指令`/usr/bin/google-chrome-stable --user-data-dir=<data_dir>/1`
  2. 安装Tampermonkey拓展
  3. 打开 `Tampermonkey扩展` 界面新建js，拷贝`script.js`中的内容之后<kbd>Ctrl+S</kbd>
  4. 更改浏览器保存路径为`/twitter_user_tweet_crawler/output/res`
  5. ...依次类推，直至全部配置完毕
## 运行
1. 在有`pyproject.toml`的上级目录运行指令
```commandline
poetry run python3 -m twitter_user_tweet_crawler
```
2. 登录推特
3. 按下回车键
4. Done.
