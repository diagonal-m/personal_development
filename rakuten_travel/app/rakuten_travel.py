"""
楽天トラベルからスクレイピングをするスクリプト
docker run -it --rm -v $(pwd):/root chrome bash
"""
import re
import traceback
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


RAKUTEN_TRAVEL = "https://travel.rakuten.co.jp/"
MAX_WAIT_TIME = 5
PREFECTURES = ['茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '神奈川県', '東京都', '山梨県', '静岡県', '長野県']
CHECK_IN = '2020/09/19'
CHECK_OUT = '2020/09/20'


def select_option(driver: webdriver, css_selector: str, text: str) -> None:
    """
    select要素のoptionを選択する(クリックとは方法が異なる)
​
    @param driver: 使われるドライバー
    @param css_selector: select要素のcssセレクター e.g.) '#shopContractList'
    @param text: optionの中で選択したいテキスト  e.g.) [包括契約]楽天カード株式会社
    """
    element = WebDriverWait(driver, MAX_WAIT_TIME).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, css_selector)
        )
    )  # そのセレクターが「見える」まで、最大MAX_WAIT_TIME秒待つ
    Select(element).select_by_visible_text(text)  # option要素の表示テキストで選択する


def input_text(driver: webdriver, css_selector: str, text: str) -> None:
    """
    css_selectorが指定する位置にtextを入力する

    @param driver: 使われるドライバー
    @param css_selector: textを入力する位置をcssセレクターで指定 e.g.) '#main >td:nth-child(2) > input[type=text]'
    @param text: 入力するテキスト e.g.) 'atd000832601'
    """
    element = WebDriverWait(driver, MAX_WAIT_TIME).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, css_selector)
        )
    )  # そのセレクターが「見える」まで、最大MAX_WAIT_TIME秒待つ
    element.clear()  # 現在の文字を消す
    element.send_keys(text)
    element.send_keys(Keys.ENTER)


def get_text(driver: webdriver, css_selector: str) -> str:
    """
    css_selectorが指定する位置からtextを取得する

    @param driver: 使われるドライバー
    @param css_selector: textを取得する位置をcssセレクターで指定
    @return: 取得したtext
    """
    element = WebDriverWait(driver, MAX_WAIT_TIME).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, css_selector)
        )
    )  # そのセレクターが「見える」まで、最大MAX_WAIT_TIME秒待つ
    return element.text


def get_attribute(driver: webdriver, css_selector: str, attribute: str = 'src') -> str:
    """
    css_selectorが指定する位置からattributeで指定した属性値を取得する

    @param driver: 使われるドライバー
    @param css_selector: 取得したい属性値の位置をcss_selectorで指定
    @param attribute: 取得したい属性を指定 (default: 'src')
    @return: 属性値
    """
    element = WebDriverWait(driver, MAX_WAIT_TIME).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, css_selector)
        )
    )  # そのセレクターが「見える」まで、最大MAX_WAIT_TIME秒待つ
    return element.get_attribute(attribute)


def click(driver: webdriver, css_selector: str) -> None:
    """
    要素をクリックするする

    @param driver: 使われるドライバー
    @param css_selector: クリックする位置をcssのセレクターで指定
    """
    element = WebDriverWait(driver, MAX_WAIT_TIME).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, css_selector)
        )
    )  # そのセレクターが「クリックできる状態になる」まで、最大MAX_WAIT_TIME秒待つ
    element.click()


def check(driver: webdriver, xpath: str) -> None:
    """
    チェックボックスにチェックを入れる

    @param driver: 使われるドライバー
    @param xpath: チェックを入れる位置をxpathで指定
    """
    element = WebDriverWait(driver, MAX_WAIT_TIME).until(
        EC.visibility_of_element_located(
            (By.XPATH, xpath)
        )
    )  # そのxpathが「チェックできる状態になる」まで、最大MAX_WAIT_TIME秒待つ
    element.click()


def create_driver() -> webdriver:
    """
    webdriverを作成する

    @return: webdriver
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Firefox(options=options)

    driver.get(RAKUTEN_TRAVEL)
    sleep(1)
    click(driver, '#cat01 > a')
    sleep(1)
    input_text(driver, '#dh-checkin', CHECK_IN)
    sleep(1)
    input_text(driver, '#dh-checkout', CHECK_OUT)
    sleep(1)
    click(driver, '#kokunaiSearch')
    sleep(1)

    return driver


def option_check(driver: webdriver, option_list: list) -> None:
    """
    指定のオプションにチェックを入れる
    @param driver: webdriver
    @param option_list: 指定のオブションのリスト
    """
    option_dict = {
        '高級宿': '//*[@id="premium"]',
        '朝食あり': '//*[@id="breakfast"]',
        '夕食あり': '//*[@id="dinner"]',
        '送迎バス': '//*[@id="pubus"]',
        '露天風呂': '//*[@id="rot"]',
        '貸切風呂': '//*[@id="fam"]',
        '露天風呂付き客室': '//*[@id="roten"]'
    }
    for option, x_path in option_dict.items():
        if option in option_list:
            check(driver, x_path)
            sleep(1)
    click(driver, '#dh-squeeze-submit')


def error(driver) -> bool:
    """
    検索結果が見つからなかったときTrueを返す
    @param driver:
    @return: エラーかどうかのbool値
    """
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    error_area = soup.find('div', id='errorArea')

    return bool(error_area)


def fetch_travel_info(driver: webdriver, prefecture: str, area: str) -> pd.DataFrame:
    """
    宿情報を取得して返す
    @param driver: 使用するドライバー
    @param prefecture: 都道府県
    @param area: 地域
    @return: 宿情報のデータフレーム
    """
    try:
        WebDriverWait(driver, MAX_WAIT_TIME).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '#htlBox')
            )
        )
    except Exception:
        print('空室なし')
        return pd.DataFrame()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    hotel_list = [a.find('a').text for a in soup.find_all('h2')]
    link_list = [a.find('a').attrs['href'] for a in soup.find_all('h2')]

    return pd.DataFrame({
        '都道府県': [prefecture] * len(hotel_list),
        '地域': [area] * len(hotel_list),
        'ホテル': hotel_list,
        'URL': link_list
    })


def main() -> None:
    """
    メイン処理
    """
    info_df = pd.DataFrame()
    driver = create_driver()
    try:
        option_check(driver, ['露天風呂'])
        for prefecture in PREFECTURES:
            # 宿泊地: 都道府県を選択
            print(prefecture)
            select_option(driver, '#dh-middle', prefecture)
            sleep(1)
            # 地域のリストを取得
            areas = get_text(driver, '#dh-small').split('\n')[1:]
            for area in areas:
                # 宿泊地: 地域を選択
                print(area)
                if area == '東京２３区内':
                    continue
                select_option(driver, '#dh-small', area)
                sleep(1)
                click(driver, '#dh-submit')
                sleep(1)
                info_df = info_df.append(
                    fetch_travel_info(driver, prefecture, area)
                )
    except Exception:
        traceback.print_exc()
        driver.quit()
        return
    driver.quit()
    info_df.to_csv('露天風呂.csv', encoding='cp932', index=None)
    print('出力完了')


if __name__ == '__main__':
    main()
