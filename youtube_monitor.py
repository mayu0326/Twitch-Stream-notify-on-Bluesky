# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

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

from version_info import __version__
import time
import requests
from threading import Thread, Event
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __version__


class YouTubeMonitor(Thread):
    """
    YouTubeライブ配信および動画投稿の新着を監視するスレッド。
    """

    def __init__(
            self,
            api_key,
            channel_id,
            poll_interval,
            on_live,
            on_new_video,
            shutdown_event=None):
        # APIキー、チャンネルID、ポーリング間隔、コールバック関数を初期化
        super().__init__(daemon=True)
        self.api_key = api_key
        self.channel_id = channel_id
        self.poll_interval = poll_interval
        self.on_live = on_live
        self.on_new_video = on_new_video
        self.last_live_status = False
        self.last_video_id = None
        self.shutdown_event = shutdown_event if shutdown_event is not None else Event()

    def run(self):
        # スレッドのメインループ。shutdown_eventがセットされたら安全に終了
        while not self.shutdown_event.is_set():
            try:
                # ライブ配信の有無を確認
                live = self.check_live()
                if live and not self.last_live_status:
                    self.on_live(live)
                self.last_live_status = live

                # 新着動画の有無を確認
                video_id = self.get_latest_video_id()
                if video_id and video_id != self.last_video_id:
                    self.on_new_video(video_id)
                    self.last_video_id = video_id

            except Exception as e:
                print(f"[YouTubeMonitor] エラー発生: {e}")
            self.shutdown_event.wait(self.poll_interval)

    def check_live(self):
        """
        チャンネルで現在ライブ配信中かどうかを判定。
        """
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&channelId={self.channel_id}&eventType=live&type=video&key={self.api_key}"
        )
        resp = requests.get(url)
        data = resp.json()
        return len(data.get("items", [])) > 0

    def get_latest_video_id(self):
        """
        チャンネルの最新動画IDを取得。
        """
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&channelId={self.channel_id}&order=date&type=video&key={self.api_key}&maxResults=1"
        )
        resp = requests.get(url)
        data = resp.json()
        items = data.get("items", [])
        if items:
            return items[0]["id"]["videoId"]
        return None
