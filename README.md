> [!NOTE]
> Note: Downloading the audio in tweets is not supported yet.

> [!WARNING]
> Do not leak your `cookie.json`, this will lead to your Twitter account being stolen.

![](https://github.com/kaixinol/twitter_user_tweet_crawler/actions/workflows/python-app.yaml/badge.svg)

## Introduction
- This tool can automatically simulate browser operations to crawl all users' tweets and save all static resources (videos, pictures) locally without calling the Twitter API.
- At the same time, sqlite3 is used to save the crawled data as an index file for easy query.
## Install
### Install dependencies
- Install `Python3.10+`
- Install `Poetry`
- Install `Chrome 119.0+`
- Run the command `poetry install` in the directory with `pyproject.toml`
### Prepare configuration
- Configure `config.yaml`
- Edit line 69 of `/twitter_user_tweet_crawler/__main__.py`
- Prepare Chrome user data folder <i><u> (set data_dir to `/twitter_user_tweet_crawler/userdata/` as an example)</u></i>
   1. Create a new folder under `/twitter_user_tweet_crawler/userdata/`
   2. If you need ***n browser instances at the same time***, create ***n+1 folders***
   3. For example, you need 3 threads to work at the same time
   4. Just create new `/twitter_user_tweet_crawler/userdata/1` `/twitter_user_tweet_crawler/userdata/2` `/twitter_user_tweet_crawler/userdata/3` `/twitter_user_tweet_crawler/userdata/4`
- Pre-configured Chrome
   1. Execute the command `/usr/bin/google-chrome-stable --user-data-dir=<data_dir>/1`
   2. Install Tampermonkey extension
   3. Open the `Tampermonkey extension` interface to create a new js, copy the content in `script.js`<kbd>Ctrl+S</kbd>
   4. Change the browser save path to `/twitter_user_tweet_crawler/output/res`
   5. ...and so on until all configurations are completed
## Run
1. Run the command in the upper-level directory with `pyproject.toml`
```commandline
poetry run python3 -m twitter_user_tweet_crawler
```
2. Log in to Twitter
3. Press the Enter key
4. Done.