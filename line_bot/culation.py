"""
line botメッセージ作成のためのクラス(newsサイトculation)
"""
import datetime
from time import sleep
import requests
from bs4 import BeautifulSoup

from typing import Dict


def get_datetime_now() -> datetime:
    """
    main.pyを実行した日付を取得し返す関数
    @return: datetimeオブジェクト
    """
    dt = datetime.datetime.now()
    return dt


def response_soup(base_url: str) -> BeautifulSoup:
    """
    urlを引数にスープ型を返す関数
    @param base_url: url
    @return:soup型
    """
    response = requests.get(base_url)
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, 'html.parser')

    return soup


class NewsCulation:
    """
    newsキュレーションクラス
    """
    def __init__(self, message_text: str):
        """
        初期化メソッド
        """
        self.site_no = int(message_text.split(' ')[1])
        self.to_day = get_datetime_now()

    def get_news_techcrunch(self, base_url: str) -> Dict:
        """
        techcrunchから一日の記事タイトルとそのURLの辞書型を返す関数

        @param base_url: 元となるURL
        @return: 記事タイトル: 記事URLの辞書
        """
        news_dict = dict()  # 記事タイトルと記事URLを格納する空の辞書
        page = 1
        # 年月日をサイトの仕様に変換
        target_day = f'{self.to_day:%Y}年{self.to_day.month}月{self.to_day.day}日'
        # クローリング＆スクレイピング
        while page > 0:
            soup = response_soup(base_url.format(page))

            news_blocks = soup.find_all('li', class_='river-block')

            for news_block in news_blocks:
                news_day = news_block.find('time')  # 記事が投稿された日付を取得

                # main関数実行日時に投稿された記事のみ取得
                if news_day is not None:
                    news_day = news_day.text
                    if news_day != target_day:
                        page = -1
                        break
                    else:
                        # 記事タイトルと記事URLを取得し辞書に格納
                        news_title = news_block.find('h2', class_='post-title').find('a')
                        title_name = news_title.text
                        news_url = news_title.attrs['href']
                        news_dict[title_name] = news_url
                else:
                    continue
            if page == -1:
                break
            else:
                page += 1
                sleep(1)

        return news_dict

    def get_news_forbesjapan(self, base_url) -> Dict:
        """
        forbesjapanからmain関数実行日時の記事タイトルとそのURLの辞書型を返す関数

        @param base_url: 元なるURL
        @return: 記事タイトル：記事URLの辞書
        """
        news_dict = dict()  # 記事タイトルと記事URLを格納する空の辞書
        page = 0
        # 年月日をサイトの仕様に変換
        target_day = f'{self.to_day:%Y/%m/%d}'

        # クローリング＆スクレイピング
        while page >= 0:
            soup = response_soup(base_url.format(page))

            class_1 = 'stream-article et-promoblock-removeable-item et-promoblock-star-item clearfix'
            news_blocks = soup.find_all('li', class_=class_1)

            for news_block in news_blocks:
                news_day = news_block.find('time', class_='article-time')

                # main関数実行日時に投稿された記事のみ取得
                news_day = news_day.text
                if news_day.find(target_day) < 0:
                    page = -1
                    break
                else:
                    # 記事タイトルと記事URLを取得し辞書に格納
                    news_title = news_block.find('h2', class_='fs-h2 article-headline').find('span')
                    title_name = news_title.text
                    news_url = news_block.find('a').attrs['href']
                    news_dict[title_name] = news_url

            if page < 0:
                break
            else:
                page += 1
                sleep(1)

        return news_dict

    @staticmethod
    def get_news_itmedia(base_url) -> Dict:
        """
        itmediaから一日の記事タイトルとそのURLの辞書型を返す関数

        @param base_url: 元となるURL
        @return: 記事タイトル：記事URLの辞書
        """
        news_dict = dict()  # 記事タイトルと記事URLを格納する空の辞書

        # クローリング＆スクレイピング
        soup = response_soup(base_url)
        class_1 = 'colBox colBoxBacknumber'
        class_2 = 'colBoxIndex'
        news_titles = soup.find('div', class_=class_1).find('div', class_=class_2).find_all('a')

        for news_title in news_titles:
            title_name = news_title.text
            news_url = news_title.attrs['href']
            news_dict[title_name] = news_url

        return news_dict

    def get_news_ainow(self, base_url) -> Dict:
        """
        AINOWから一日の記事タイトルとそのURLを返す関数

        @param base_url: 元となるURL
        @return: 記事タイトル：記事URLの辞書
        """
        news_dict = dict()
        page = 1
        # 年月日をサイトの仕様に変換
        target_day = self.to_day.strftime("%Y.%m.%d")

        # クローリング＆スクレイピング
        while page > 0:
            soup = response_soup(base_url.format(page))

            news_blocks = soup.find(
                'div', class_='main_article_area', id='new_article_area'
            ).find_all('article', class_='article')

            for news_block in news_blocks:
                news_day = news_block.find('span', class_='article_date')
                news_day = news_day.text

                if news_day.find(target_day) < 0:
                    page = -1
                    break
                else:
                    news_title = news_block.find('div', class_='article_title').find('h2')
                    title_name = news_title.text
                    news_url = news_block.find('a').attrs['href']
                    news_dict[title_name] = news_url

            if page < 0:
                break
            else:
                page += 1
                sleep(1)

        return news_dict

    def join_news_dict(self) -> Dict:
        """
        各スクレイピングメソッドをまとめて実行し、返り値の辞書を結合して返す

        @return: 記事タイトルとurlの辞書
        """

        # クローリング関数の辞書
        get_news = {
            0: {
                'craw_name': self.get_news_techcrunch,
                'args': {'base_url': 'https://jp.techcrunch.com/page/{}/'}
            },
            1: {
                'craw_name': self.get_news_forbesjapan,
                'args': {'base_url': 'https://forbesjapan.com/articles/lists/{}0'}
            },
            2: {
                'craw_name': self.get_news_itmedia,
                'args': {'base_url': 'https://www.itmedia.co.jp/news/subtop/archive/'}
            },
            3: {
                'craw_name': self.get_news_ainow,
                'args': {'base_url': 'https://ainow.ai/page/{}/'}
            }
        }

        news_dict = get_news[self.site_no]['craw_name'](**get_news[self.site_no]['args'])

        return news_dict

    def create_message(self) -> str:
        """
        newsキュレーションクラスのメイン関数
        @return: 送信するメッセージ
        """
        message_text = str()
        news_dict = self.join_news_dict()
        for title, url in news_dict.items():
            message_text += f'・{title[:20]}\n{url}\n'

        return message_text
