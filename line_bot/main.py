"""
line botメインスクリプト
"""

from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from study import StudySetting
from culation import NewsCulation
from consts import YOUR_CHANNEL_ACCESS_TOKEN, YOUR_CHANNEL_SECRET, DATABASE, USER_0, USER_1

import os

app = Flask(__name__)

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


class HelpMassage:
    """
    ヘルプクラス
    """
    def __init__(self, message_text: str):
        """
        初期化メソッド

        @param message_text: 受け取ったメッセージテキスト
        """
        self._ = message_text

    @staticmethod
    def create_message():
        """
        helpメッセージ
        """
        message = "study\n" \
                  "名字 目標○h: １日の目標勉強時間をセット\n" \
                  "名字 スタート: ストップウォッチを起動する\n" \
                  "名字 ストップ: ストップウォッチを停止する\n" \
                  "名字 END: 目標時間に対する評価\n" \
                  "名字 week: 週の合計勉強時間\n" \
                  "culation\n" \
                  "news 0: TechCrunch\n" \
                  "news 1: forbesjapan\n" \
                  "news 2: itmedia\n" \
                  "news 3: ainow"

        return message


def select_class(message_text: str) -> type:
    """
    受け取ったメッセージを元に対応するクラスを返す関数

    @param message_text: 受け取ったメッセージ
    @return: メッセージに対応するクラス
    """
    key_message = message_text.split(' ')[0]
    class_dict = {
        'help': HelpMassage,
        USER_0: StudySetting, USER_1: StudySetting,
        'news': NewsCulation
    }

    return class_dict[key_message]


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


def reply_message(event, message: str) -> None:
    """
    メッセージテキストを受け取って、送信する関数

    @param event: イベント
    @param message: 送信するテキスト
    """
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message_text = event.message.text
    # 受け取ったメッセージに従ってクラスを選択する
    try:
        selected_class = select_class(message_text)
    except KeyError:
        return
    sc = selected_class(message_text)
    message = sc.create_message()
    reply_message(event, message[:2000])


if __name__ == "__main__":
    # app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
