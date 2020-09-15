"""
line botメッセージ作成のためのクラス(学習計画)
"""
import re
import pandas as pd
import psycopg2

from datetime import datetime

from consts import DATABASE, USER_0, USER_1


def get_h_m_s(td: float):
    """
    秒数から時、分、秒を計算する関数

    @param td: 秒数
    @return: 時、分、秒
    """
    m, s = divmod(td, 60)
    h, m = divmod(m, 60)
    return h, m, s


class StudySetting:
    """
    勉強時間クラス
    """
    def __init__(self, message_text: str):
        """
        初期化メソッド
        @param message_text: 受け取ったメッセージテキスト
        """
        self.message_text = message_text  # 受け取ったメッセージ
        self.name = message_text.split(' ')[0]  # 送信者の名前
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _get_data_from_db(self, column: str):
        """
        データベースから指定されたデータを取得して返す関数
        @param column: カラム名
        @return: 取得したデータ
        """
        with psycopg2.connect(**DATABASE) as conn:
            sql = "select * from study where name = '{}';"
            df = pd.read_sql(sql.format(self.name), conn)
            return df[column].values[0]

    def _update_db(self, column: str, data):
        """
        データベースのデータを変更する関数

        @param column: カラム名
        @param data: 変更後のデータ
        """
        with psycopg2.connect(**DATABASE) as conn:
            cur = conn.cursor()
            sql = "update study set {} = {} where name = '{}';"
            cur.execute(sql.format(column, data, self.name))

    def _update_db_str(self, column: str, data):
        """
        データベースのデータを変更（str）

        @param column: カラム名
        @param data: 変更後のデータ
        """
        with psycopg2.connect(**DATABASE) as conn:
            cur = conn.cursor()
            sql = "update study set {} = '{}' where name = '{}';"
            cur.execute(sql.format(column, data, self.name))

    def setting_target_time(self) -> str:
        """
        受け取ったメッセージをもとに１日の目標勉強時間を設定する関数
        e.g.) 佐藤 目標2h

        @return: 送信するメッセージ
        """
        if len(self.message_text.split(' ')) != 2:
            return 'は？'

        # 目標時間を取得
        if 'h' in self.message_text:
            target_time = self.message_text.split(' ')[1].replace('目標', "").replace('h', "")
        else:
            target_time = self.message_text.split(' ')[1].replace('目標', "")

        # メッセージが目標止まりの場合は設定した目標時間を通知する
        if not target_time:
            target_time = self._get_data_from_db('target')
            t_h, t_m, _ = get_h_m_s(target_time)
            return f'{self.name}の本日の目標勉強時間は{int(t_h)}時間{int(t_m)}分です'

        # 経過時間をリセット、目標時間を更新
        self._update_db("elapsed_time", 0.0)
        self._update_db("target", float(target_time) * 3600)

        h, m, s = get_h_m_s(float(target_time) * 3600)

        return f'{self.name}は本日{int(h)}時間{int(m)}分勉強することを宣言しました'

    def setting_start_time(self) -> str:
        """
        〇〇 スタート、のメッセージをキーに起動する関数
        勉強開始の日時を記録する
        e.g.) 佐藤 スタート

        @return: 送信するメッセージ
        """
        # メッセージバリデーション
        if len(self.message_text.split(' ')) != 2:
            return 'は？'

        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        switch = self._get_data_from_db("switch")
        if switch:
            return f'タイマーが起動されています'
        self._update_db_str("start", start_time)
        self._update_db("switch", True)

        return 'お勉強タイムスタート！\n頑張れー！！'

    def cal_remaining_time(self) -> str:
        """
        〇〇 ストップ、のメッセージをキーに起動する関数
        勉強実施時間を計算して、目標時間までの残り時間を計算する

        @return: メッセージテキスト
        """
        # メッセージバリデーション
        if len(self.message_text.split(' ')) != 2:
            return 'は？'

        stop_time = datetime.now()

        switch = self._get_data_from_db("switch")
        if not switch:
            return 'タイマーが起動されていません'
        start_time = datetime.strptime(str(self._get_data_from_db('start'))[:-10], '%Y-%m-%dT%H:%M:%S')
        study_time = (stop_time - start_time).total_seconds()
        elapsed_time = self._get_data_from_db("elapsed_time") + study_time
        remaining_time = self._get_data_from_db("target") - elapsed_time
        # 一週間あたりの勉強時間を計算
        week_time = self._get_data_from_db("week") + study_time
        self._update_db('elapsed_time', elapsed_time)
        self._update_db('week', week_time)
        self._update_db('switch', False)

        s_h, s_m, _ = get_h_m_s(study_time)
        re_h, re_m, _ = get_h_m_s(abs(remaining_time))

        if remaining_time >= 0:
            return f'{int(s_h)}時間{int(s_m)}分勉強して、\n目標勉強時間まで残り{int(re_h)}時間{int(re_m)}分!\n頑張れー！'
        else:
            return f'{int(s_h)}時間{int(s_m)}分勉強して、\n目標勉強時間よりも{int(abs(re_h))}時間{int(re_m)}分超えました！\nまだまだいけるぞー！'

    def evaluation_study(self) -> str:
        """
        1日の勉強時間を評価してメッセージ文字列を返す関数

        @return: 送信用テキスト
        """
        # メッセージバリデーション
        if len(self.message_text.split(' ')) != 2:
            return 'は？'

        target_time = self._get_data_from_db('target')
        elapsed_time = self._get_data_from_db('elapsed_time')
        self._update_db('elapsed_time', 0.0)
        e_h, e_m, _ = get_h_m_s(elapsed_time)
        diff = target_time - elapsed_time
        d_h, d_m, _ = get_h_m_s(abs(diff))

        if datetime.now().weekday() == 6:
            w_h, w_m, _ = get_h_m_s(self._get_data_from_db("week"))
            self._update_db('week', 0)
            return f"本日は{int(e_h)}時間{int(e_m)}分勉強して\n週合計{int(w_h)}時間{int(w_m)}分勉強しました。\n 来週も頑張れー！！"

        if diff >= 0:
            return f'本日は{int(e_h)}時間{int(e_m)}分勉強しました。\n目標時間に{int(d_h)}時間{int(d_m)}分足りません。\n今日１日何してたんだ？'
        else:
            return f'本日は{int(e_h)}時間{int(e_m)}分勉強しました。\n目標時間より{int(d_h)}時間{int(d_m)}分多く勉強しました！。\n目標設定が甘いんじゃないか？'

    def total_week_study_time(self) -> str:
        """
        月~日の合計勉強時間を計算する

        @return: 送信用メッセージ
        """
        # メッセージバリデーション
        if len(self.message_text.split(' ')) != 2:
            return 'は？'
        week = self._get_data_from_db('week')
        w_h, w_m, _ = get_h_m_s(week)

        return f'{self.name}は今週{int(w_h)}時間{int(w_m)}分勉強してます。'

    def create_message(self):
        """
        受け取ったメッセージによって返すメッセージを分岐させる関数
        @return: 各関数
        """
        # 目標時間設定
        pattern = re.compile(f'^[{USER_0}|{USER_1}\s]+目標')
        if pattern.match(self.message_text):
            return self.setting_target_time()

        # タイマースタート
        pattern = re.compile(f'^[{USER_0}|{USER_1}\s]+スタート')
        if pattern.fullmatch(self.message_text):
            return self.setting_start_time()

        # タイマーストップ
        pattern = re.compile(f'^[{USER_0}|{USER_1}\s]+ストップ')
        if pattern.fullmatch(self.message_text):
            return self.cal_remaining_time()

        # 勉強時間評価
        pattern = re.compile(f'^[{USER_0}|{USER_1}\s]+END')
        if pattern.match(self.message_text):
            return self.evaluation_study()

        # 一週間の合計勉強時間
        pattern = re.compile(f'^[{USER_0}|{USER_1}\s]+week')
        if pattern.fullmatch(self.message_text):
            return self.total_week_study_time()
