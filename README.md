> [!WARNING]
> Do not leak your `cookie.json`, this will lead to your Twitter account being stolen.

![](https://github.com/kaixinol/twitter_user_tweet_crawler/actions/workflows/python-app.yaml/badge.svg)

## Introduction
- This tool can automatically simulate browser operations to crawl all users' tweets and save all static resources (videos, pictures) locally without calling the Twitter API.
- At the same time, sqlite3 is used to save the crawled data as an index file for easy query.
## Installation & Configuration
- Install `Python3.10+`
- Install `Poetry`
- Install `Chrome 119.0+`
- Run the command `poetry install` in the directory with `pyproject.toml`
- Configure `config.yaml`
## Run
1. Run the command in the upper-level directory with `pyproject.toml`
```commandline
poetry run python3 -m twitter_user_tweet_crawler
```
2. Log in to Twitter
3. Press the Enter key
4. Done.