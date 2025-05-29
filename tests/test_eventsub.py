# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

from eventsub import verify_signature
from version_info import __version__

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __version__


# Stream notify on Bluesky
# Copyright (C) 2025 mayuneco(mayunya)
#
# このプログラムはフリーソフトウェアです。フリーソフトウェア財団によって発行された
# GNU 一般公衆利用許諾契約書（バージョン2またはそれ以降）に基づき、再配布または
# 改変することができます。
#
# このプログラムは有用であることを願って配布されていますが、
# 商品性や特定目的への適合性についての保証はありません。
# 詳細はGNU一般公衆利用許諾契約書をご覧ください。
#
# このプログラムとともにGNU一般公衆利用許諾契約書が配布されているはずです。
# もし同梱されていない場合は、フリーソフトウェア財団までご請求ください。
# 住所: 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


class DummyRequest:
    def __init__(self, headers, body):
        # テスト用のダミーリクエストオブジェクトを初期化
        self.headers = headers
        self.body = body  # 本文データ

    def get_data(self, as_text=None):
        # 本文データを取得（as_text=Trueならstr, それ以外はbytesで返す）
        if as_text:
            return self.body
        return self.body.encode("utf-8")

    @property
    def remote_addr(self):
        # ダミーのリモートアドレス
        return "127.0.0.1"


def test_verify_signature_missing_headers():
    # 必須ヘッダーが不足している場合はFalseを返すことを確認
    req = DummyRequest(headers={}, body="{}")
    assert not verify_signature(req)


def test_verify_signature_invalid_timestamp():
    # 不正なタイムスタンプの場合はFalseを返すことを確認
    headers = {
        "Twitch-Eventsub-Message-Id": "abc",
        "Twitch-Eventsub-Message-Timestamp": "invalid",  # パースできないタイムスタンプ
        "Twitch-Eventsub-Message-Signature": "sig"
    }
    req = DummyRequest(headers=headers, body="{}")
    assert not verify_signature(req)
