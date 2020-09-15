"""
定数格納ファイル
"""
import os

# 環境変数取得
# LINE API
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
# データベース
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_PORT = os.environ["DB_PORT"]
DB_USER = os.environ["DB_USER"]
DB_NAME = os.environ["DB_NAME"]
DB_HOST = os.environ["DB_HOST"]

# データベース情報
DATABASE = {"dbname": DB_NAME, "host": DB_HOST, 'user': DB_USER,
            "password": DB_PASSWORD, "port": DB_PORT}

# ユーザ名
USER_0 = os.environ["USER_NAME_0"]
USER_1 = os.environ["USER_NAME_1"]
