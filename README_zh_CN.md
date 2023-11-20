> [!WARNING]
> 不要泄漏自己的`cookie.json`，这将导致你的推特账号被盗。

![](https://github.com/kaixinol/twitter_user_tweet_crawler/actions/workflows/python-app.yaml/badge.svg)

## 简介
- 此工具能够自动的模拟浏览器操作爬取用户的全部推文并将全部静态资源(视频、图片)保存在本地,无需调用Twitter API
- 同时利用sqlite3将爬取到的数据保存为索引文件，方便查询。
## 安装 & 配置
- 安装`Python3.10+`
- 安装`Poetry`
- 安装`Chrome 119.0+`
- 在有`pyproject.toml`的目录运行指令`poetry install`
- 配置`config.yaml`
## 运行
1. 在有`pyproject.toml`的上级目录运行指令
```commandline
poetry run python3 -m twitter_user_tweet_crawler
```
2. 登录推特
3. 按下回车键
4. Done.
